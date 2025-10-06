#!/usr/bin/env python
"""
Скрипт для запуска всех компонентов системы
"""
import subprocess
import sys
import time
import os
from multiprocessing import Process

def run_django():
    """Запуск Django сервера"""
    subprocess.run([sys.executable, "run_server.py"])

def run_celery():
    """Запуск Celery worker"""
    subprocess.run([sys.executable, "run_celery.py"])

def run_telegram_bot():
    """Запуск Telegram бота"""
    subprocess.run([sys.executable, "run_telegram_bot.py"])

def run_periodic_tasks():
    """Запуск периодических задач"""
    import django
    from django.conf import settings
    from celery.schedules import crontab
    from task_manager.celery import app
    
    # Настраиваем периодические задачи
    app.conf.beat_schedule = {
        'check-overdue-tasks': {
            'task': 'notifications.tasks.check_overdue_tasks',
            'schedule': crontab(minute=0, hour='*/1'),  # Каждый час
        },
    }
    
    # Запускаем Celery beat
    subprocess.run([sys.executable, "-m", "celery", "-A", "task_manager", "beat", "--loglevel=info"])

if __name__ == "__main__":
    print("Запуск системы управления задачами...")
    print("Компоненты:")
    print("- Django сервер (порт 8000)")
    print("- Celery worker")
    print("- Telegram бот")
    print("- Периодические задачи")
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        # Запускаем все компоненты
        processes = []
        
        # Django сервер
        p1 = Process(target=run_django)
        p1.start()
        processes.append(p1)
        
        # Celery worker
        p2 = Process(target=run_celery)
        p2.start()
        processes.append(p2)
        
        # Telegram бот
        p3 = Process(target=run_telegram_bot)
        p3.start()
        processes.append(p3)
        
        # Периодические задачи
        p4 = Process(target=run_periodic_tasks)
        p4.start()
        processes.append(p4)
        
        # Ждем завершения всех процессов
        for p in processes:
            p.join()
            
    except KeyboardInterrupt:
        print("\nОстановка системы...")
        for p in processes:
            p.terminate()
        print("Система остановлена.")
