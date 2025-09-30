"""Общие клавиатуры бота.

В тои числе клавиатура для Inline Query.
"""

from collections.abc import Iterator

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.types import InlineQueryResultArticle as InlineArticle
from aiogram.types import InlineQueryResultPhoto as InlinePhoto
from aiogram.types import InputTextMessageContent as InputText
from mau.deck.behavior import WildTakeBehavior
from mau.game.game import MauGame
from mau.game.player import Player
from mau.game.player_manager import PlayerManager

from mautg.messages import game_status

# Когда кто-то пробует использовать inline режим бота без активной комнаты
NO_GAME_QUERY = InlineArticle(
    id="nogame",
    title="В чате ещё нет игровой комнаты",
    input_message_content=InputText(
        message_text=(
            "☕ Сейчас никто не играет.\n\n"
            "Используйте /game для создания новой комнаты.\n"
            "А после воспользуйтесь /join чтобы присоединиться к комнате. "
        ),
    ),
)


SHOTGUN_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Взять 🃏", callback_data="shot_take"),
            InlineKeyboardButton(text="🔫 Выстрелить", callback_data="shot"),
        ],
    ],
)

NEW_GAME_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍪 Новая игра", callback_data="new_game")],
    ],
)


def hand_query(player: Player) -> Iterator[InlinePhoto]:
    """Возвращает основную клавиатуру с игровыми действиями."""
    player_cards = player.cover_cards()
    for i, card in player_cards.cover:
        yield InlinePhoto(
            id=f"{i}",
            photo_url=f"https://mau.miroq.ru/card/next/{card.pack()}/cover",
            thumbnail_url=f"https://mau.miroq.ru/card/next/{card.pack()}/cover",
            photo_width=64,
            photo_height=128,
            description=card.pack(),
        )

    for i, card in player_cards.uncover:
        yield InlinePhoto(
            id=f"status:{i}",
            photo_url=f"https://mau.miroq.ru/card/next/{card.pack()}/uncover",
            thumbnail_url=f"https://mau.miroq.ru/card/next/{card.pack()}/uncover",
            input_message_content=InputText(
                message_text=game_status(player.game),
            ),
            photo_width=64,
            photo_height=128,
            description=card.pack(),
        )


# Inline клавиатура
# =================


def select_player(pm: PlayerManager, skip_button: bool) -> InlineKeyboardMarkup:
    """Клавиатура для выбора игрока.

    Содержит имя игрока и сколько у него сейчас карт.
    """
    res = [
        [
            InlineKeyboardButton(
                text=f"{pl.name} ({len(pl.hand)} 🃏)",
                callback_data=f"select_player:{pl.user_id}",
            ),
        ]
        for i, pl in pm.iter_others()
    ]

    if skip_button:
        res.append(
            [InlineKeyboardButton(text="🍷 Пропустить", callback_data="next")],
        )

    return InlineKeyboardMarkup(inline_keyboard=res)


def lobby_markup(game: MauGame) -> InlineKeyboardMarkup:
    """Вспомогательная клавиатура для управления комнатой.

    Позволяет начать игру и присоединиться к ней.
    А также открыть клавиатуру для настройки игровых правил.
    """
    buttons = [
        [
            InlineKeyboardButton(text="🪄 Правила", callback_data="room_rules"),
            InlineKeyboardButton(text="🃏 Колода", callback_data="deck_edit"),
        ],
        [
            InlineKeyboardButton(text="☕ Зайти", callback_data="join"),
        ],
    ]
    if len(game.pm) >= game.min_players:
        buttons[0].append(
            InlineKeyboardButton(
                text="🎮 Начать игру", callback_data="start_game",
            ),
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def turn_markup(
    game: MauGame, take_button: bool = True,
) -> InlineKeyboardMarkup:
    """Клавиатура для хода."""
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🎮 Разыграть 🃏",
                switch_inline_query_current_chat="",
            ),
        ],
    ]

    if take_button:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🃏 взять", callback_data="take")],
        )
    else:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🍓 завершить", callback_data="next")],
        )

    if (
        isinstance(game.deck.top.behavior, WildTakeBehavior)
        and game.take_counter
    ):
        inline_keyboard[-1].append(
            InlineKeyboardButton(text="🍷 блефуешь", callback_data="bluff"),
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def color_markup(game: MauGame) -> InlineKeyboardMarkup:
    """Собирает клавиатуру для выбора цвета."""
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    for c in game.deck.colors:
        if c.value % 4 == 0:
            inline_keyboard.append([])
        inline_keyboard[-1].append(
            InlineKeyboardButton(text=c.emoji, callback_data=f"color:{c.value}"),
        )

    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="🃏 Ваши карты", switch_inline_query_current_chat="",
            ),
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
