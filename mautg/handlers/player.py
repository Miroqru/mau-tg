"""Взаимодействие пользователя с игровыми комнатами.

Присоединение, отключение.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from mau.deck.behavior import TakeBehavior, WildTakeBehavior
from mau.game.game import MauGame
from mau.game.player import BaseUser, Player

from mautg import filters
from mautg.events.journal import MessageChannel

router = Router(name="Player")


@router.message(Command("join"), filters.ActiveGame())
async def join_player(message: Message, game: MauGame) -> None:
    """Подключает пользователя к игре."""
    if message.from_user is None:
        raise ValueError("User can`t be none")

    player = game.join_player(
        BaseUser(
            str(message.from_user.id),
            message.from_user.first_name,
            message.from_user.mention_html(),
        ),
    )
    if player is None:
        await message.answer(
            "🔒 К сожалению данная комната <b>закрыта</b>.\n"
            "Вы можете попросить владельца комнаты открыть"
            "комнату или дождаться окончания игра.",
        )


@router.message(Command("leave"), filters.ActivePlayer())
async def leave_player(message: Message, player: Player) -> None:
    """Выход пользователя из игры."""
    player.game.leave_player(player)


@router.callback_query(F.data == "join", filters.ActiveGame())
async def join_callback(query: CallbackQuery, game: MauGame) -> None:
    """Добавляет игрока в текущую комнату."""
    if not isinstance(query.message, Message):
        raise ValueError("Query message should be Message instance")

    player = game.join_player(
        BaseUser(
            str(query.from_user.id),
            query.from_user.first_name,
            query.from_user.mention_html(),
        ),
    )
    if player is None:
        await query.answer("🔒 К сожалению данная комната <b>закрыта</b>.")
    else:
        await query.answer("👋 Добро пожаловать в комнату")


@router.callback_query(F.data == "shot_take", filters.NowPlaying())
async def take_cards_call(
    query: CallbackQuery, game: MauGame, player: Player, channel: MessageChannel,
) -> None:
    """Игрок выбирает взять карты."""
    if game.player == player:
        channel.add("🃏 Вы решили что будет проще <b>взять карты</b>.")
    else:
        game.pm.set_cp(player)
        channel.add(f"🃏 {player.mention} решил <b>взять карты</b>.")

    take_counter = game.take_counter
    player.take_cards()

    # Если пользователь сам взял карты, то не нужно пропускать ход
    # TODO: Отвязаться от типов карт
    if (
        isinstance(game.deck.top.behavior, TakeBehavior | WildTakeBehavior)
        and take_counter
    ):
        game.next_turn()
    else:
        channel.add(f"☕ {game.player.mention} <b>продолжает</b>.")
        await channel.send()


@router.callback_query(F.data == "shot", filters.NowPlaying())
async def shotgun_call(
    query: CallbackQuery, game: MauGame, player: Player, channel: MessageChannel,
) -> None:
    """Игрок выбирает взять карты."""
    res = player.shot()
    if not res:
        game.take_counter = round(game.take_counter * 1.5)
        channel.add(
            "✨ На сей раз <b>вам повезло</b> и револьвер не выстрелил.\n"
            f"🃏 Следующий игрок берёт <b>{game.take_counter} карт</b>!\n",
        )
        await channel.send()
        if game.player != player:
            game.pm.set_cp(player)
        game.end_turn(player)
    else:
        if game.player == player:
            channel.add("😴 На этом игра для вас <b>закончилась</b>.\n")
        else:
            channel.add(f"😴 {player.mention} попал под пулю..\n")
        game.leave_player(player)
