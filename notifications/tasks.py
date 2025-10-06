"""
Celery tasks for notifications.
"""
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Notification
from tasks.models import Task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification(user_id, notification_type, title, message, task_id=None):
    """
    Отправляет уведомление пользователю
    """
    try:
        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id) if task_id else None
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            task=task
        )
        
        logger.info(f"Notification created for user {user.username}: {title}")
        return f"Notification sent to {user.username}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User with id {user_id} not found"
    except Task.DoesNotExist:
        logger.error(f"Task with id {task_id} not found")
        return f"Task with id {task_id} not found"
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def check_overdue_tasks():
    """
    Проверяет просроченные задачи и отправляет уведомления
    """
    now = timezone.now()
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['pending', 'in_progress']
    )
    
    notifications_sent = 0
    for task in overdue_tasks:
        # Отправляем уведомление исполнителю
        send_notification.delay(
            user_id=task.assigned_to.id,
            notification_type='task_overdue',
            title='Просроченная задача',
            message=f'Задача "{task.title}" просрочена. Срок выполнения: {task.due_date.strftime("%d.%m.%Y %H:%M")}',
            task_id=task.id
        )
        notifications_sent += 1
    
    logger.info(f"Sent {notifications_sent} overdue task notifications")
    return f"Sent {notifications_sent} overdue task notifications"


@shared_task
def send_telegram_notification(chat_id, message):
    """
    Отправляет уведомление через Telegram
    """
    try:
        from telegram_bot.bot import send_message_to_user
        send_message_to_user(chat_id, message)
        logger.info(f"Telegram notification sent to chat {chat_id}")
        return f"Telegram notification sent to chat {chat_id}"
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")
        return f"Error: {str(e)}"
