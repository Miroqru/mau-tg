"""Управляет игровыми сессиями.

Позволяет создавать комнаты, удалять их, переключать настройки.
Если вас интересует взаимодействий игроков в сессиями, то перейдите
в роутер `player`.
"""

import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from mau.game.game import MauGame
from mau.game.player import BaseUser
from mau.session import SessionManager

from mautg import filters, markups
from mautg.events.journal import MessageChannel
from mautg.messages import game_status

router = Router(name="Sessions")


# Когда недостаточно игроков для продолжения/начала игры
def _not_enough_message(min_players: int) -> str:
    return (
        f"🌳 <b>Недостаточно игроков</b> (минимум {min_players}) для "
        "игры.\n"
        "Если игра ещё <b>не началась</b> воспользуйтесь командой "
        "/join чтобы зайти в комнату.\n"
        "🍰 Или создайте новую комнату при помощи /game."
    )


@router.message(Command("game"))
async def create_game(
    message: Message,
    sm: SessionManager,
    game: MauGame | None,
    channel: MessageChannel,
) -> None:
    """Создаёт новую комнату."""
    if message.chat.type == "private":
        await message.answer("👀 Игры создаются в групповом чате.")

    if game is not None:
        if game.started:
            await message.answer(
                "🔑 Игра уже начата. Для начала её нужно завершить. (/stop)",
            )
        else:
            channel.lobby_message = None
            await channel.send_lobby(
                game_status(game),
                reply_markup=markups.lobby_markup(game),
            )
        return

    if message.from_user is None:
        raise ValueError("None User tries create new game")

    # TODO: Указывать какую игру создавать
    sm.create(
        str(message.chat.id),
        BaseUser(
            str(message.from_user.id),
            message.from_user.first_name,
            message.from_user.mention_html(),
        ),
    )


@router.message(Command("start_game"), filters.ActiveGame())
async def start_gama(message: Message, game: MauGame) -> None:
    """Запускает игру в комнате."""
    if message.chat.type == "private":
        return

    if game.started:
        await message.answer("👀 Игра уже началась ранее.")

    elif len(game.pm) < game.min_players:
        await message.answer(_not_enough_message(game.min_players))

    else:
        game.start()


@router.message(Command("stop"), filters.GameOwner())
async def stop_gama(message: Message, game: MauGame) -> None:
    """Принудительно завершает текущую игру."""
    game.end()
    if message.from_user is None:
        raise ValueError("User can`t be none to stop game")

    mention = message.from_user.mention_html()
    await message.answer(f"⚡ {mention} завершает игру.")


@router.message(Command("open"), filters.GameOwner())
async def open_gama(message: Message, game: MauGame) -> None:
    """Открывает игровую комнату для всех участников чата."""
    game.open = True
    await message.answer(
        "🍰 Комната <b>открыта</b>!\n любой участник может зайти (/join).",
    )


@router.message(Command("close"), filters.GameOwner())
async def close_gama(message: Message, game: MauGame) -> None:
    """Закрывает игровую комнату для всех участников чата."""
    game.open = False
    await message.answer(
        "🔒 Комната <b>закрыта</b>.\nНикто не помешает вам доиграть.",
    )


@router.message(Command("kick"), filters.GameOwner())
async def kick_player(
    message: Message, game: MauGame, channel: MessageChannel,
) -> None:
    """Выкидывает участника из комнаты."""
    if (
        message.reply_to_message is None
        or message.reply_to_message.from_user is None
    ):
        raise ValueError(
            "🍷 Перешлите сообщение негодника, которого нужно исключить.",
        )

    kicked_user = message.reply_to_message.from_user
    kick_player = game.pm.get_or_none(str(kicked_user.id))
    if kick_player is not None:
        channel.add(
            f"🧹 {game.owner.name} выгнал "
            f"{kick_player.mention} из игры за плохое поведение.\n",
        )
        game.leave_player(kick_player)
        await channel.send()


@router.message(Command("skip"), filters.GameOwner())
async def skip_player(
    message: Message, game: MauGame, channel: MessageChannel,
) -> None:
    """пропускает участника за долгое бездействие."""
    game.take_counter += 1
    game.player.take_cards()
    skip_player = game.player
    channel.add(
        f"☕ {skip_player.mention} потерял свои ку.. карты.\n"
        "Мы их нашли и дали игроку ещё немного карт от нас.\n",
    )
    # Иногда может быть такое, что пропускается чёрная карта
    # Тогда ей нужно дать какой-нибудь цвет
    if game.deck.top.color == game.deck.wild_color:
        game.choose_color(random.choice(game.deck.colors))
    else:
        game.next_turn()


@router.callback_query(F.data == "new_game")
async def create_game_call(
    query: CallbackQuery, sm: SessionManager, game: MauGame | None,
) -> None:
    """Создаёт новую комнату."""
    if query.message is None or query.from_user is None:
        raise ValueError("None User tries create new game")

    if game is not None:
        await query.answer("🔑 Игра уже начата. Для начала её нужно завершить.")
        return

    game = sm.create(
        str(query.message.chat.id),
        BaseUser(
            str(query.from_user.id),
            query.from_user.first_name,
            query.from_user.mention_html(),
        ),
    )
    await query.answer("Понеслась!")


@router.callback_query(F.data == "start_game", filters.ActiveGame())
async def start_game_call(query: CallbackQuery, game: MauGame) -> None:
    """Запускает игру в комнате."""
    if not isinstance(query.message, Message):
        raise ValueError("Query.message is not a Message")
    game.start()
