# 🚀 Быстрый запуск системы управления задачами

## Установка и запуск за 5 минут

### 1. Установка зависимостей

```bash
# Установка Python зависимостей
pip install -r requirements.txt

# Установка PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Установка Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Или используйте Docker
docker-compose up -d db redis
```

### 2. Настройка окружения

```bash
# Копируем файл окружения
cp env.example .env

# Редактируем настройки
nano .env
```

Минимальные настройки в `.env`:
```env
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/task_manager
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=your-bot-token-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Настройка базы данных

```bash
# Создание базы данных PostgreSQL
sudo -u postgres createdb task_manager

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 4. Запуск системы

```bash
# Запуск всех компонентов одной командой
python run.py
```

Или запуск компонентов отдельно:

```bash
# Терминал 1: Django сервер
python run_server.py

# Терминал 2: Celery worker
python run_celery.py

# Терминал 3: Telegram бот (опционально)
python run_telegram_bot.py
```

### 5. Настройка Telegram-бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен и добавьте в `.env` файл
3. Перезапустите систему
4. Найдите бота в Telegram и отправьте `/start`
5. В веб-приложении перейдите в настройки профиля
6. Скопируйте ваш Chat ID и введите в профиле

## 🎯 Использование

### Веб-приложение
- Откройте http://localhost:8000
- Зарегистрируйтесь или войдите
- Создайте список задач
- Добавьте задачи и назначьте исполнителей

### Telegram-бот
- `/start` - начать работу
- `/link` - привязать аккаунт
- `/tasks` - показать задачи
- `/overdue` - показать просроченные

## 🔧 Решение проблем

### Ошибка подключения к базе данных
```bash
# Проверьте, что PostgreSQL запущен
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Ошибка подключения к Redis
```bash
# Проверьте, что Redis запущен
sudo systemctl status redis
sudo systemctl start redis
```

### Ошибки миграций
```bash
# Сброс миграций (ОСТОРОЖНО!)
python manage.py migrate --fake-initial
```

### Проблемы с Telegram-ботом
- Проверьте токен в `.env` файле
- Убедитесь, что бот запущен
- Проверьте логи в консоли

## 📱 Docker запуск

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 🎉 Готово!

Система управления задачами запущена и готова к использованию!

- **Веб-приложение**: http://localhost:8000
- **Админ-панель**: http://localhost:8000/admin
- **API документация**: http://localhost:8000/api/

### Следующие шаги:
1. Создайте пользователей
2. Настройте списки задач
3. Привяжите Telegram-бот
4. Начните управлять задачами!
