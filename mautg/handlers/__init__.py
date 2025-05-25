"""Инициализация всех обработчиков.

Весь функционал бота был поделён на обработчики для большей гибкости.
"""

from mautg.handlers import (
    deck,
    donut,
    player,
    rules,
    session,
    simple_commands,
    turn,
)

# Список всех работающих роутеров
ROUTERS = (
    deck.router,
    donut.router,
    player.router,
    rules.router,
    session.router,
    simple_commands.router,
    turn.router,
)

__all__ = ("ROUTERS",)
