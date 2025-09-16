"""Простые вспомогательные команды для бота."""

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from loguru import logger

router = Router(name="simple commands")

STATUS_MESSAGE = (
    "🌟 <b>Немного о Mau v2.3</b>:\n\n"
    "🃏 Это Telegram бот для игры с друзьями в групповом чате.\n"
    "Поддерживается множество игровых правил для большего веселья.\n"
    "Исходный код проекта доступен в:\n"
    "- <a href='https://git.miroq.ru/salormoon/mauno'>Miroq</a>\n"
    "- <a href='https://github.com/miroqru/mauno'>Github</a>.\n"
    "📖 <a href='https://mau.miroq.ru/docs/'>Документация</a>."
    "🎀 <b>Генератор карт</b> и использованные асета "
    "<a href='https://git.miroq.ru/rumia/mau-cards'>Тут</a>\n\n"
    "🌱 Мы будем очень рады ваше <b>поддержке</b> в развитие бота.\n\n"
    "🪄 Следить за новостями можно в канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)

# Когда пользователь пишет сообщение /help
# Немного рассказывает про бота и как им пользоваться
HELP_MESSAGE = (
    "🍰 <b>Три простых шага чтобы начать веселье</b>!\n\n"
    "1. Добавьте бота в вашу группу.\n"
    "2. В группе создайте комнату через /game или зайдите в неё через /join.\n"
    "3. Как только все собрались, начинайте игру при помощи /start!\n"
    "4. Введите <code>@mili_mautg</code> в чате или жмякните на кнопку хода.\n"
    "Здесь все ваши карты, а ещё кнопки чтобы взять карты и "
    "проверить текущее состояние игры.\n"
    "<b>Серые</b> карты вы пока не можете разыграть.\n"
    "Нажмите на один из стикеров карты, чтобы разыграть её.\n\n"
    "🌳 Игроки могут подключиться в любое время.\n"
    "Если не хотите чтобы вам помешали, закройте комнату через /close.\n"
    "Чтобы покинуть игру используйте /leave.\n"
    "Если игрок долго думает. его можно пропустить командой /skip.\n"
    "☕ О прочих командах можно узнать в <b>меню</b>.\n"
)


@router.message(Command("help"))
async def get_help(message: Message, bot: Bot) -> None:
    """Помогает пользователю начать работать с ботом."""
    if message.chat.type == "private":
        await message.answer(HELP_MESSAGE)
        return

    try:
        await message.delete()
    except Exception as e:
        logger.warning("Unable to delete message: {}", e)
        await message.answer(
            "👀 Пожалуйста выдайте мне права удалять сообщения в чате."
        )

    try:
        if message.from_user is not None:
            await bot.send_message(message.from_user.id, HELP_MESSAGE)
            await message.answer("✨ Помощь отправлена в личные сообщения.")
    except Exception as e:
        logger.warning("Unable to send private message: {}", e)
        await message.answer("👀 Я не могу написать вам первым.")


@router.message(Command("status"))
async def get_bot_status(message: Message) -> None:
    """Полезная информация о боте."""
    await message.answer(STATUS_MESSAGE)


@router.message(CommandStart())
async def start_bot(message: Message) -> None:
    """Начало диалога с ботом."""
    await message.answer(HELP_MESSAGE)
