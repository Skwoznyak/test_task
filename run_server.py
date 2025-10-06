#!/usr/bin/env python
"""
Скрипт для запуска Django сервера с поддержкой WebSocket
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
    django.setup()
    
    # Запускаем миграции
    execute_from_command_line(["manage.py", "migrate"])
    
    # Создаем суперпользователя если его нет
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Создан суперпользователь: admin/admin123")
    
    # Запускаем сервер
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])
