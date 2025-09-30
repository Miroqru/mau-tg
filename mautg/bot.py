"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import asyncio
import secrets
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Annotated, Any

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.methods import TelegramMethod
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    ErrorEvent,
    InlineQuery,
    Message,
    Update,
)
from aiogram.utils.token import TokenValidationError
from fastapi import APIRouter, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from mautg.config import config, default, sm
from mautg.context import get_context
from mautg.events.journal import MessageJournal
from mautg.events.router import er
from mautg.handlers import ROUTERS

dp = Dispatcher(sm=sm)

# Настраиваем формат отображения логов loguru
# Обратите внимание что в проекте помимо loguru используется logging
LOG_FORMAT = (
    "<light-black>{time:YYYY MM.DD HH:mm:ss.SSS}</> "
    "{file}:{function} "
    "<lvl>{message}</>"
)

# Middleware
# ==========


@dp.message.middleware()  # type: ignore
@dp.inline_query.middleware()  # type: ignore
@dp.callback_query.middleware()  # type: ignore
@dp.chat_member.middleware()  # type: ignore
@dp.chosen_inline_result.middleware()  # type: ignore
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Callable[[Update, dict[str, Any]], Awaitable[Any]]:
    """Предоставляет экземпляр игры в обработчики сообщений."""
    if isinstance(
        event, CallbackQuery | ChosenInlineResult | InlineQuery | Message,
    ):
        context = get_context(sm, event)
        data["game"] = context.game
        data["player"] = context.player
        data["channel"] = (
            sm._event_handler.get_channel(context.game.room_id)
            if context.game is not None
            else None
        )

    return await handler(event, data)


@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message
    else:
        message = None

    if message is None:
        logger.warning("No Message to send exception")
        return

    await message.answer(
        f"👀 <b>Что-то пошло не по плану</b>...\n{event.exception}",
    )


# Настройка webhook
# =================


async def on_startup(bot: Bot) -> None:
    """Настройка webhook при запуске."""
    logger.info("Set hook to: {}", config.hook_url)
    await bot.set_webhook(
        f"{config.hook_url}{config.hook_root}", secret_token=config.hook_secret,
    )


async def on_shutdown(bot: Bot) -> None:
    """Настройка webhook при запуске."""
    logger.info("Stop bot")
    await bot.session.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл бота."""
    workflow_data = {
        "app": app,
        "dispatcher": dp,
        **dp.workflow_data,
    }

    # db connected
    await dp.emit_startup(**workflow_data)

    yield

    # app teardown
    await dp.emit_shutdown(**workflow_data)


router = APIRouter()


@router.post(config.hook_root)
async def process_hook(
    update: Update,
    secret: Annotated[
        str, Header(alias="x-telegram-bot-api-secret-token"),
    ] = "",
) -> dict:
    """Обрабатывает приходящие события для бота."""
    if not secrets.compare_digest(secret, config.hook_secret):
        raise HTTPException(401, "Unauthorized")

    result: TelegramMethod[Any] | None = await dp.feed_webhook_update(
        dp.workflow_data["bot"], update,
    )

    if not result:
        return {}

    logger.debug(result)
    return {}


#     writer = MultipartWriter(
#         "form-data", boundary=f"webhookBoundary{secrets.token_urlsafe(16)}"
#     )

#     payload = writer.append(result.__api_method__)
#     payload.set_content_disposition("form-data", name="method")

#     files: dict[str, InputFile] = {}
#     for key, value in result.model_dump(warnings=False).items():
#         value = bot.session.prepare_value(value, bot=bot, files=files)
#         if not value:
#             continue
#         payload = writer.append(value)
#         payload.set_content_disposition("form-data", name=key)

#     for key, value in files.items():
#         payload = writer.append(value.read(bot))
#         payload.set_content_disposition(
#             "form-data",
#             name=key,
#             filename=value.filename or key,
#         )

#     return StreamingResponse(writer, media_type="multipart/form-data")


# Запуск бота
# ===========


def create_app(router: APIRouter) -> FastAPI:
    """Запускает работу Webhook."""
    app: FastAPI = FastAPI(
        debug=True,
        title="Mau:bot",
        summary="Play Mau with your friends in telegram chats",
        version="2.2",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


def main() -> None:
    """Запускает бота.

    Настраивает журнал действий.
    Загружает все необходимые обработчики.
    После запускает обработку событий бота.
    """
    logger.remove()
    logger.add(sys.stdout, format=LOG_FORMAT)

    logger.info("Setup bot ...")
    try:
        bot = Bot(config.telegram_token.get_secret_value(), default=default)
    except TokenValidationError as e:
        logger.error(e)
        sys.exit("Check your bot token in .env file.")

    logger.info("Load handlers ...")
    for r in ROUTERS:
        dp.include_router(r)
        logger.debug("Include router {}", r.name)

    logger.info("Set event handler")
    sm.set_handler(MessageJournal(bot, er))

    logger.success("Start polling!")
    if config.use_hook:
        dp.workflow_data["bot"] = bot
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        app = create_app(router)
        uvicorn.run(app, host=config.server_host, port=config.server_port)
    else:
        asyncio.run(dp.start_polling(bot))
