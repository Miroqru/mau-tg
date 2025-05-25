# Mau;tg

<img src="./assets/logo.png" width="256"></img>

[![License](https://img.shields.io/badge/License-AGPL%20v3-red?style=flat&labelColor=%23B38B74&color=%23FF595F)](./LICENSE)
![Bot version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.version&prefix=v&style=flat&label=Mau&labelColor=%23B38B74&color=%2373FFAD)
![Python version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.requires-python&style=flat&logo=python&logoColor=%23B38B74&label=python&labelColor=%23805959&color=%232185A6)
[![Docs](https://img.shields.io/badge/docs-miroq-%2300cc99?style=flat&labelColor=%23805959&color=%2330BFB3&link=https%3A%2F%2Fmau.miroq.ru%2Fdocs%2F)](https://mau.miroq.ru/docs/)
![GitHub stars](https://img.shields.io/github/stars/miroqru/mau-tg?style=flat&logo=github&logoColor=%23E6D0A1&label=Stars&labelColor=%23805959&color=%23FFF766)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Mau;tg** - Telegram бот для совместной игры в
[mau](https://github.com/miroqru/mauno) с друзьями в групповых чатах.

**Немного особенностей**:

- 🎮 **Легко** научиться играть
- 🍓 Много необычных и весёлых **игровых правил**
- ☕ Система **Лобби**
- 🌟 Несколько вариантов **колод**
- 📝 **Журнал** игровых событий
- 🃏 Красивые нарисованные карточки

> Бот использует `inline query` клавиатуру для карт.
> Будьте готовы что после игры остаётся *море сообщений* в чате.
> Зато это же так весело!


## Начинаем играть

[![Telegram](./assets/banner.png)](https://t.me/mau_room)

Если вы заинтересованы, то давайте же **сыграем вместе**!

**Поиграть с нами** можно здесь: [@mau_room](https://t.me/mau_room).

Вот ссылочка на основного бота: [@mili_maubot](https://t.me/mili_maubot).
Ещё можете подписаться на канал [Salormoon](https://t.me/mili_qlaster),
чтобы следить за обновлениями проекта и прочими новостями команды.

**Всё что нужно знать для начала игры**:

1. **Добавляем** бота в чат с друзьями
2. Вводим `/game` для создания **нового лобби**
3. Когда все игроки присоединились, **нажимаем** начать (`/start_game`)
4. Весело **играем** партию
5. Ошалеваем от количества сообщений и безудержного веселья
6. Создаём ещё одну комнатку и повторяем с 3 шага

> Ознакомиться с полным списком команд вы можете в *меню* бота.
> На самом деле основных команд не так уж и много.

## Поднимаем своего бота
Разумеется благодаря открытому коду вы можете запустить **своего бота**.
Для работы с зависимостями и виртуальным окружением используется
[uv](https://docs.astral.sh/uv/).

1. Клонируем репозиторий:

```sh
git clone https://github.com/miroqru/mau-tg
```

2. Устанавливаем зависимости:

```sh
uv sync
```

3. Копируем файл с настройками `.env.dist` в `.env`
4. Вставляем в файл токен от бота
4. Запускаем бота:

```sh
uv run -m maubot
```

Ах да, ещё вам потребуется включить `inline mode` для вашего бота и
обязательно выставить `inline feedback` на 100%.
Сделать это в [BotFather](https://t.me/BotFather).
Без этого, отправленные вами карты не будут обрабатываться ботом.

## Переход на mauren

**Mauren** - это новый клиент для доступа к серверу Mau.
Новый сервер добавляет больше игровых возможностей и делает API более
стабильный чем прямое использование движка.

## Поддержка проекта

Мы будем очень рады, если вы **поддержите развитие проекта**.
Есть несколько способов как вы можете это сделать:

- Оставить **звёздочку** в репозитории.
- **Играть** вместе с друзьями в Mau.
- **Участвовать в бета-тестировании** новых функций.
- **Предлагать** свои собственные идеи.
- Сообщать о найденных багах или даже предлагать их решение.
- **Сделать** форк проекта.

> Подробности в [документации](https://mau.miroq.ru/docs/use/maintenance)

Нам бы очень хотелось создать **лучшего бота** для весёлой совместной игры с друзьями!
