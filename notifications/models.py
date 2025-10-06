"""
Models for notifications.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """Модель для уведомлений"""
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Назначена задача'),
        ('task_completed', 'Задача выполнена'),
        ('task_overdue', 'Задача просрочена'),
        ('task_updated', 'Задача обновлена'),
        ('comment_added', 'Добавлен комментарий'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Пользователь")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Тип уведомления")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата прочтения")
    
    # Связь с задачей (опционально)
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Задача")
    
    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Отмечает уведомление как прочитанное"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
