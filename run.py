#!/usr/bin/env python
"""
Единый скрипт для запуска системы управления задачами
"""
import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process
import threading


def run_command(command, name):
    """Запуск команды в отдельном процессе"""
    try:
        print(f"Запуск {name}...")
        result = subprocess.run(command, shell=True, check=True)
        print(f"{name} завершен с кодом {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка в {name}: {e}")
    except KeyboardInterrupt:
        print(f"Остановка {name}...")


def check_dependencies():
    """Проверка зависимостей"""
    print("Проверка зависимостей...")

    # Проверяем Python
    if sys.version_info < (3, 8):
        print("Ошибка: Требуется Python 3.8 или выше")
        sys.exit(1)

    # Проверяем наличие файла .env
    if not os.path.exists('.env'):
        print("Создание файла .env из шаблона...")
        if os.path.exists('env.example'):
            with open('env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("Файл .env создан. Отредактируйте его перед запуском.")
        else:
            print("Ошибка: Файл env.example не найден")
            sys.exit(1)

    print("Зависимости проверены ✓")


def setup_database():
    """Настройка базы данных"""
    print("Настройка базы данных...")

    try:
        # Применяем миграции
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("Миграции применены ✓")

        # Создаем суперпользователя если его нет
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 'admin@example.com', 'admin123')
            print("Создан суперпользователь: admin/admin123 ✓")

    except Exception as e:
        print(f"Ошибка настройки базы данных: {e}")
        sys.exit(1)


def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 СИСТЕМА УПРАВЛЕНИЯ ЗАДАЧАМИ")
    print("=" * 60)
    print()

    # Проверяем зависимости
    check_dependencies()

    # Настраиваем Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

    try:
        import django
        django.setup()
        setup_database()
    except Exception as e:
        print(f"Ошибка инициализации Django: {e}")
        print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
        sys.exit(1)

    print()
    print("Компоненты системы:")
    print("• Django сервер (http://localhost:8000)")
    print("• Celery worker (фоновые задачи)")
    print("• Telegram бот (если настроен токен)")
    print("• Периодические задачи")
    print()
    print("Для остановки нажмите Ctrl+C")
    print("=" * 60)
    print()

    # Список процессов
    processes = []

    try:
        # Запускаем Django сервер
        p1 = Process(target=run_command, args=(
            "python run_server.py", "Django сервер"))
        p1.start()
        processes.append(p1)

        # Небольшая задержка
        time.sleep(2)

        # Запускаем Celery worker
        p2 = Process(target=run_command, args=(
            "python run_celery.py", "Celery worker"))
        p2.start()
        processes.append(p2)

        # Проверяем наличие токена Telegram
        from django.conf import settings
        if hasattr(settings, 'TELEGRAM_BOT_TOKEN') and settings.TELEGRAM_BOT_TOKEN:
            # Запускаем Telegram бот
            p3 = Process(target=run_command, args=(
                "python run_telegram_bot.py", "Telegram бот"))
            p3.start()
            processes.append(p3)
        else:
            print("⚠️  TELEGRAM_BOT_TOKEN не настроен. Telegram бот не будет запущен.")

        # Запускаем периодические задачи
        p4 = Process(target=run_command, args=(
            "celery -A task_manager beat --loglevel=info", "Периодические задачи"))
        p4.start()
        processes.append(p4)

        print("✅ Все компоненты запущены!")
        print("🌐 Веб-приложение: http://localhost:8000")
        print("📱 Telegram бот: найдите вашего бота в Telegram")
        print()

        # Ждем завершения всех процессов
        for p in processes:
            p.join()

    except KeyboardInterrupt:
        print("\n🛑 Остановка системы...")
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=5)
        print("✅ Система остановлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
