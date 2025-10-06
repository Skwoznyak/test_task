#!/usr/bin/env python
"""
Скрипт для запуска Telegram бота
"""
import os
import django
import asyncio

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
    django.setup()
    
    from telegram_bot.bot import run_bot
    run_bot()
