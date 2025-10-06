# Система управления задачами

Веб-приложение и Telegram-бот для управления задачами в команде с поддержкой работы в реальном времени и уведомлений.

## Функциональность

### Веб-приложение
- ✅ Аутентификация и регистрация пользователей
- ✅ Создание и управление списками задач
- ✅ Назначение исполнителей и установка сроков
- ✅ Отметка задач как выполненных
- ✅ Работа в реальном времени через WebSocket
- ✅ Уведомления в браузере
- ✅ Современный адаптивный интерфейс

### Telegram-бот
- ✅ Аутентификация через привязку аккаунта
- ✅ Просмотр назначенных задач
- ✅ Отметка задач как выполненных
- ✅ Уведомления о просроченных задачах
- ✅ Интеграция с веб-приложением

### Технические особенности
- ✅ Django + Django REST Framework
- ✅ Django Channels для WebSocket
- ✅ Celery для фоновых задач
- ✅ Redis для очередей и кэширования
- ✅ PostgreSQL для данных
- ✅ Aiogram для Telegram-бота
- ✅ Чистый JavaScript без фреймворков

## Установка и запуск

### Требования
- Python 3.8+
- PostgreSQL
- Redis
- Telegram Bot Token

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
```

Отредактируйте `.env` файл:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/task_manager
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Настройка базы данных

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 4. Запуск системы

#### Вариант 1: Запуск всех компонентов одной командой

```bash
python start_all.py
```

#### Вариант 2: Запуск компонентов отдельно

В разных терминалах:

```bash
# 1. Django сервер
python run_server.py

# 2. Celery worker
python run_celery.py

# 3. Telegram бот
python run_telegram_bot.py

# 4. Периодические задачи (опционально)
celery -A task_manager beat --loglevel=info
```

### 5. Настройка Telegram-бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен и добавьте в `.env` файл
3. Запустите бота командой `/start`
4. В веб-приложении перейдите в настройки профиля
5. Скопируйте ваш Chat ID и введите в профиле

## Использование

### Веб-приложение

1. Откройте http://localhost:8000
2. Зарегистрируйтесь или войдите
3. Создайте список задач
4. Добавьте задачи и назначьте исполнителей
5. Отслеживайте прогресс в реальном времени

### Telegram-бот

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Привяжите аккаунт командой `/link`
4. Используйте команды:
   - `/tasks` - показать задачи
   - `/overdue` - показать просроченные
   - `/help` - справка

## API Endpoints

### Аутентификация
- `POST /api/auth/login/` - вход
- `POST /api/auth/logout/` - выход
- `POST /api/auth/register/` - регистрация

### Задачи
- `GET /api/tasks/` - список задач
- `POST /api/tasks/` - создание задачи
- `GET /api/tasks/{id}/` - детали задачи
- `PATCH /api/tasks/{id}/` - обновление задачи
- `POST /api/tasks/{id}/mark_completed/` - отметить как выполненную

### Списки задач
- `GET /api/task-lists/` - список списков
- `POST /api/task-lists/` - создание списка

### Уведомления
- `GET /api/notifications/` - список уведомлений
- `POST /api/notifications/{id}/mark_read/` - отметить как прочитанное

## WebSocket

Подключение: `ws://localhost:8000/ws/tasks/`

События:
- `task_notification` - уведомление о задаче
- `tasks_data` - обновление списка задач

## Структура проекта

```
task_manager/
├── task_manager/          # Основные настройки Django
├── tasks/                 # Приложение для задач
├── notifications/         # Приложение для уведомлений
├── telegram_bot/         # Telegram-бот
├── templates/            # HTML шаблоны
├── static/               # Статические файлы
├── requirements.txt       # Зависимости
├── run_server.py        # Запуск Django
├── run_celery.py        # Запуск Celery
├── run_telegram_bot.py  # Запуск бота
└── start_all.py         # Запуск всех компонентов
```

## Разработка

### Добавление новых функций

1. Создайте модели в соответствующих приложениях
2. Добавьте сериализаторы в `serializers.py`
3. Создайте ViewSet в `views.py`
4. Обновите URL-маршруты
5. Добавьте фронтенд логику в шаблоны

### Тестирование

```bash
# Запуск тестов
python manage.py test

# Запуск с покрытием
coverage run --source='.' manage.py test
coverage report
```

## Развертывание

### Docker (рекомендуется)

```bash
# Сборка образа
docker-compose build

# Запуск
docker-compose up -d
```

### Продакшн

1. Установите PostgreSQL и Redis
2. Настройте переменные окружения
3. Соберите статические файлы: `python manage.py collectstatic`
4. Запустите с помощью Gunicorn и Daphne
5. Настройте Nginx для проксирования

## Лицензия

MIT License

## Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все сервисы запущены
3. Проверьте настройки в `.env` файле
4. Создайте issue в репозитории
