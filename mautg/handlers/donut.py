"""Донат на поддержку проекта."""

from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery
from loguru import logger
from pydantic import BaseModel

router = Router(name="Donut")

DONUT_PATH = Path("donuts.json")


class Donut(BaseModel):
    """Описание поддержавших проект."""

    name: str
    amount: int


class DonutInfo(BaseModel):
    """Файл со всеми донами.

    В будущем это всё конечно же будет через базу данных на сервере.
    Сейчас просто на скорую руку.
    """

    version: int
    donuts: dict[int, Donut]


def _load_donuts(donut_path: Path) -> DonutInfo:
    if not donut_path.exists():
        logger.warning("{} not found", donut_path)
        return DonutInfo(version=1, donuts={})

    with donut_path.open() as f:
        return DonutInfo.model_validate_json(f.read())


def _write_donuts(donut_path: Path, donuts: DonutInfo) -> None:
    with donut_path.open("W") as f:
        f.write(donuts.model_dump_json())


def _donut_leaders(donut_info: DonutInfo) -> str:
    res = ""
    for i, d in enumerate(
        sorted(donut_info.donuts.values(), key=lambda d: d.amount, reverse=True),
    ):
        res += f"{i + 1}. {d.name}: {d.amount}🌟"

    return res


def _donut_message(donut_info: DonutInfo) -> str:
    return (
        "🍩 <b>Поддержка</b>\n"
        "Благодаря вашей поддержке проект может продолжать развиваться.\n\n"
        "Приятной вам игры. ❤️"
        f"{_donut_leaders(donut_info)}\n"
        f"🌟 /support_mau чтобы поддержка проект звёздочками."
    )


@router.message(Command("donut"))
async def donut_info(message: Message) -> None:
    """Информация о поддерживающих игроках."""
    donut_info = _load_donuts(DONUT_PATH)
    await message.answer(_donut_message(donut_info))


@router.message(Command("support_mau"))
async def donut_invoice(message: Message) -> None:
    """Совершить оплату."""
    await message.answer_invoice(
        title="Поддержка проекта",
        description="Так вы можете выразить вашу ❤️ к Mau",
        payload="mau_supporter",
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=10)],
    )


@router.pre_checkout_query()
async def call_checkout(event: PreCheckoutQuery) -> None:
    """Проводит транзакцию."""
    await event.answer(True)


@router.message(F.successful_payment)
async def finish_payment(message: Message, bot: Bot) -> None:
    """Сообщает об успешно оплате."""
    if message.from_user is None:
        raise ValueError("user can`t be None")

    donut_info = _load_donuts(DONUT_PATH)
    user = donut_info.donuts.get(
        message.from_user.id,
        Donut(name=message.from_user.mention_html(), amount=0),
    )
    user.amount += 10
    donut_info.donuts[message.from_user.id] = user
    _write_donuts(DONUT_PATH, donut_info)

    await message.answer(
        "❤️ Благодарим вас за поддержку Mau!\n"
        "Будем и дальше радовать вас новыми обновлениями. ✨",
    )
