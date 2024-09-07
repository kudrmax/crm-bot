# Бот для управления личными контактами

Данный бот создан для личного использования для управления контактами:

### Функциональные возможности

- Сохранение информации о контакте (имя, телефон, день рождения и т.д.)
- Ведение "лога" взаимодействий с человеком (запись встреч, событий в жизни, увлечений и т.д.)
- Отслеживание регулярности встреч (информирование о том, с кем давно не виделся)
- ...

### Технологии

- Backend: `FastAPI`, `Pydantic`, `Docker`, `SQLAlchemy`
- Telegram Bot: `Aiogram`, `Requests`
- Общее: `Pytest`, `Alembic`

### Архитектура

Проект разделен на два независимых компонента:

**Backend**: Написан на `FastAPI` и представляет собой API для хранения и обработки данных контактов. Его можно
использовать не только для бота, но и для других интерфейсов, например для веб-приложения.

![](/docs/swagger.png)

**Telegram Bot**: Реализован с использованием `Aiogram`. Он взаимодействует с backend через HTTP-запросы. Бот может быть
заменен другим клиентом (например, фронтендом), не затрагивая работу backend.

[ДОБАВИТЬ ФОТО]()

[//]: # (### Документация API)

[//]: # ()

[//]: # (Все endpoints задокументированы с помощью автосгенерированного Swagger: [в будущем тут будет ссылка]&#40;&#41;)

## Использование

#### Для использования

Открыть бота в телеграм: [в будущем будет ссылка на бота]()

#### Для разработчиков

Инструкция пока что не дописана.

```bash
# склонировать репозиторий
git clone ...
cd ...

# установить виртуальное окружение и зависимости
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# поднять баду данных
make up

# обновить базу данных
alembic upgrade head

# запустить backend
python3 src/main.py

# запустить бота
python3 src/bot/bot.py
```

```bash
# остановить базу данных
make down
```