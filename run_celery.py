#!/usr/bin/env python
"""
Скрипт для запуска Celery worker
"""
import os
import django
from celery import Celery

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
    django.setup()
    
    from task_manager.celery import app
    
    # Запускаем Celery worker
    app.worker_main(['worker', '--loglevel=info'])
