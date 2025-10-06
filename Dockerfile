FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Создание пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
