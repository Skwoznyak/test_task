"""
Models for task management application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TaskList(models.Model):
    """Модель для списка задач"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_task_lists', verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Список задач"
        verbose_name_plural = "Списки задач"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """Модель для задачи"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks', verbose_name="Список задач")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', verbose_name="Исполнитель")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="Создатель")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Проверяет, просрочена ли задача"""
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    def mark_completed(self):
        """Отмечает задачу как выполненную"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class TaskComment(models.Model):
    """Модель для комментариев к задачам"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name="Задача")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Комментарий к задаче {self.task.title} от {self.author.username}"


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="Telegram Chat ID")
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name="Telegram Username")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.username}"
