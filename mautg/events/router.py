"""Маршрутизация событий от движка."""

from loguru import logger
from mau.enums import CardColor, GameEvents, GameState
from mau.events import Event

from mautg import markups, messages
from mautg.config import sm
from mautg.events.journal import EventRouter, MessageChannel
from mautg.messages import plural_form

er = EventRouter()


@er.event(GameEvents.SESSION_START)
async def start_session(event: Event, chan: MessageChannel) -> None:
    """Отправляет лобби, когда начинается новая игра в чате."""
    lobby_message = (
        f"{messages.game_status(event.game)}\n\n"
        f"🔥 {event.player.name}, Начинает новую игру!"
    )
    await chan.send_lobby(
        message=lobby_message,
        reply_markup=markups.lobby_markup(event.game),
    )


# Обработка событий игры
# ======================


@er.event(GameEvents.GAME_START)
async def start_game(event: Event, chan: MessageChannel) -> None:
    """Оповещает о начале новой игры."""
    await chan.send_lobby(
        message=messages.game_status(event.game),
        reply_markup=None,
    )
    await chan.clear()
    chan.set_markup(markups.turn_markup(event.game))
    await chan.send_card(event.game.deck.top)
    chan.add("🌳 Да начнётся <b>Новая игра!</b>!")
    chan.add(f"✨ Игру начинает {event.game.player.mention}.")
    chan.add(
        f"{messages.game_rules_list(event.game)}"
        "/close если не хотите чтобы вашей игре помешали.\n",
    )
    chan.add(f"🎨 Дикий цвет: {event.game.deck.wild_color.emoji}")
    await chan.send()


@er.event(GameEvents.GAME_END)
async def end_game(event: Event, chan: MessageChannel) -> None:
    """Завершает игру в чате."""
    chan.add(messages.end_game_players(event.game.pm))
    chan.set_markup(markups.NEW_GAME_MARKUP)
    await chan.send()
    sm.remove(event.game.room_id)
    await sm._event_handler.remove_channel(event.game.room_id)


@er.event(GameEvents.GAME_JOIN)
async def join_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if not event.game.started:
        lobby_message = (
            f"{messages.game_status(event.game)}\n\n"
            f"👋 {event.player.mention} зашёл в комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=markups.lobby_markup(event.game),
        )
        return

    chan.add(f"🍰 Добро пожаловать в игру, {event.player.mention}!")
    await chan.send()


@er.event(GameEvents.GAME_LEAVE)
async def leave_player(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь вышел из игры."""
    if chan.lobby_message is not None and not event.game.started:
        lobby_message = (
            f"{messages.game_status(event.game)}\n\n"
            f"👋 {event.player.mention} покидает комнату!"
        )
        await chan.send_lobby(
            message=lobby_message,
            reply_markup=markups.lobby_markup(event.game),
        )
        return

    if event.data == "win":
        chan.add(f"👑 {event.player.mention} закончил(а)!\n")
    else:
        chan.add(f"👋 {event.player.mention} покидает нас.")

    await chan.send()


@er.event(GameEvents.GAME_SELECT_COLOR)
async def select_card_color(event: Event, chan: MessageChannel) -> None:
    """Какой новый цвет был выбран для карты."""
    chan.add(f"🎨 Я выбираю {CardColor(int(event.data)).emoji}!")


@er.event(GameEvents.GAME_SELECT_PLAYER)
async def twist_hand(event: Event, chan: MessageChannel) -> None:
    """Сообщает об обмене картами между пользователями."""
    other_player = event.game.pm.get_or_none(event.data)
    if other_player is None:
        chan.add("🍺 Куда подевался второй игрок?")
        return

    # Событие происходит после выполнения действия, потому так считаем карты
    chan.add(
        f"🤝 {event.player.name} ({len(other_player.hand)} 🃏) "
        f"и {other_player.mention} ({len(event.player.hand)} 🃏) "
        "обменялись картами.\n",
    )


@er.event(GameEvents.GAME_TURN)
async def next_turn(event: Event, chan: MessageChannel) -> None:
    """Начала следующего хода."""
    await chan.clear()
    chan.set_markup(markups.turn_markup(event.game))
    cards = len(event.game.player.hand)
    chan.add(
        f"\n🍰 <b>ход</b>: {event.game.player.mention} "
        f"(🃏 {cards} {plural_form(cards, ('карта', 'карты', 'карт'))})",
    )
    await chan.send()


@er.event(GameEvents.PLAYER_PUT)
async def push_card(event: Event, chan: MessageChannel) -> None:
    """Игрок кладёт новую карту на верх колоды."""
    chan.add(f"🎮 Кладу карту {messages.card_info(event.game.deck.top)}")
    chan.put_card = True


@er.event(GameEvents.GAME_ROTATE)
async def rotate_cards(event: Event, chan: MessageChannel) -> None:
    """Все игрока обменялись картами, возвращает сколько карт у игроков."""
    chan.add("🌀 Обмениваемся <b>картами</b>!")
    chan.add(messages.players_list(event.game.pm, event.game.reverse))


@er.event(GameEvents.GAME_STATE)
async def update_game_state(event: Event, chan: MessageChannel) -> None:
    """При изменении игрового состояния."""
    state = GameState(int(event.data))
    if state == GameState.SHOTGUN:
        chan.add(
            "💼 <b>У нас для Вас деловое предложение</b>!\n\n"
            f"Вы можете <b>взять {event.game.take_counter} карт</b> "
            "или попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать следующий игрок.\n"
            f"🔫 Из револьвера стреляли {event.game.shotgun.cur} / 8 раз\n.",
        )
        chan.set_markup(markups.SHOTGUN_MARKUP)

    elif state == GameState.TWIST_HAND:
        chan.add("✨ С кем бы обменяться картами ..")
        chan.set_markup(
            markups.select_player(
                event.game.pm,
                event.game.rules.twist_hand_pass.status,
            ),
        )

    elif state == GameState.CHOOSE_COLOR:
        chan.add("✨ Какой бы выбрать цвет ...")
        chan.set_markup(markups.color_markup(event.game))

    elif state == GameState.TAKE:
        chan.set_markup(markups.turn_markup(event.game, take_button=False))

    else:
        logger.warning("Unprocessed state {}", state)
        return

    await chan.send()


# Обработка действий игрока
# =========================


@er.event(GameEvents.PLAYER_MAU)
async def say_mau(event: Event, chan: MessageChannel) -> None:
    """Оповещает что у игрока осталась одна карта в руке."""
    chan.add("😺 <b>Mau!</b>")


@er.event(GameEvents.PLAYER_TAKE)
async def player_take_cards(event: Event, chan: MessageChannel) -> None:
    """Оповещает что пользователь взял карты."""
    if chan.lobby_message is not None:
        return

    if event.player == event.game.player:
        chan.add(
            f"🃏 Беру {event.data} "
            f"{plural_form(int(event.data), ('карту', 'карты', 'карт'))}",
        )
    else:
        chan.add(
            f"🃏 {event.player.mention} Берёт {event.data} "
            f"{plural_form(int(event.data), ('карту', 'карты', 'карт'))}",
        )

    await chan.send()


@er.event(GameEvents.PLAYER_BLUFF)
async def player_bluffing(event: Event, chan: MessageChannel) -> None:
    """Проверка игрока на блеф."""
    if event.game.bluff_player is None:
        chan.add("🎩 <b>Никто не блефовал</b>!")
        return

    player, bluff_flag = event.game.bluff_player
    if player is not None and bluff_flag:
        chan.add("🔎 <b>Замечен блеф</b>!")
    else:
        chan.add(f"🎩 {player.mention} <b>Честный игрок</b>!")


@er.event(GameEvents.PLAYER_INTERVENED)
async def on_intervention(event: Event, chan: MessageChannel) -> None:
    """Когда игрок вмешивается в игру и перехватывает ход."""
    chan.add(f"⚡ {event.player.mention} <b>навёл суеты!</b>")
    await chan.send()
