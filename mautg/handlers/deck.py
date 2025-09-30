"""Простые вспомогательные команды для бота."""

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from mau.deck.presets import CARD_PRESETS, CardGroup, DeckGenerator, DeckPreset
from mau.game.game import MauGame

from mautg.filters import GameOwner

router = Router(name="Deck editor")

# Сообщений
# =========


def get_presets(
    presets: dict[str, DeckPreset], now_preset: str,
) -> InlineKeyboardMarkup:
    """Собирает клавиатуру доступных шаблонов колоды."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=preset.name, callback_data=f"preset:{name}",
                ),
            ]
            for name, preset in presets.items()
            if name != now_preset
        ],
    )


def get_deck_info(groups: list[CardGroup]) -> str:
    """Собирает сообщение с выбранными правилами генератора колоды."""
    res = ""
    for group in groups:
        colors = "".join(color.emoji for color in group.colors)
        res += (
            f"\n{colors} <code>{group.behavior.name}</code> "
            f"{group.value} / x{group.count}"
        )
    return res


def deck_editor_message(deck: DeckGenerator, preset: DeckPreset) -> str:
    """Собирает сообщение редактора колоды."""
    return (
        "✏️ <b>Редактор колоды</b>:\n"
        f"Шаблон: {preset.name}:\n{preset.desc}\n"
        f"{get_deck_info(deck.groups)}\n\n"
        "💡 Вы можете выбрать один из готовых <b>шаблонов</b>."
    )


# Обработчики
# ===========


@router.callback_query(F.data == "deck_edit", GameOwner())
async def get_deck_editor(query: CallbackQuery, game: MauGame) -> None:
    """Получает сообщение редактора колоды с готовыми шаблонами."""
    await query.answer()
    preset = CARD_PRESETS.get(
        game.deck_generator.preset_name,
        DeckPreset("Свой", "Время творить чудеса", []),
    )
    if query.message is None:
        raise ValueError("No callback message to answer")
    await query.message.answer(
        deck_editor_message(game.deck_generator, preset),
        reply_markup=get_presets(CARD_PRESETS, game.deck_generator.preset_name),
    )


class PresetCallback(CallbackData, prefix="preset"):
    """Клавиатура выбора шаблона колоды."""

    name: str


@router.callback_query(PresetCallback.filter(), GameOwner())
async def set_deck_preset(
    query: CallbackQuery, game: MauGame, callback_data: PresetCallback,
) -> None:
    """Выбирает один из заготовленных шаблонов колоды для игры."""
    await query.answer()
    game.deck_generator = DeckGenerator.from_preset(callback_data.name)
    preset = CARD_PRESETS.get(
        game.deck_generator.preset_name,
        DeckPreset("Свой", "Время творить чудеса", []),
    )
    if not isinstance(query.message, Message):
        raise ValueError("No callback message to edit_text")
    await query.message.edit_text(
        deck_editor_message(game.deck_generator, preset),
        reply_markup=get_presets(CARD_PRESETS, game.deck_generator.preset_name),
    )
