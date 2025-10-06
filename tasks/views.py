"""
Views for task management API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import TaskList, Task, TaskComment, UserProfile
from .serializers import (
    TaskListSerializer, TaskSerializer, TaskCreateSerializer, 
    TaskUpdateSerializer, TaskCommentSerializer, UserSerializer, UserProfileSerializer
)
from .permissions import IsOwnerOrAssigned
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class TaskListViewSet(viewsets.ModelViewSet):
    """ViewSet для управления списками задач"""
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Пользователь видит только свои списки задач
        return TaskList.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для управления задачами"""
    permission_classes = [IsAuthenticated, IsOwnerOrAssigned]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Пользователь видит задачи, где он исполнитель или создатель
        return Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).select_related('assigned_to', 'created_by', 'task_list').prefetch_related('comments__author')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Отправляем уведомление через WebSocket
        self._send_websocket_notification(serializer.instance, 'task_created')
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        instance = serializer.save()
        
        # Если статус изменился, отправляем уведомление
        if old_status != instance.status:
            self._send_websocket_notification(instance, 'task_updated')
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Отметить задачу как выполненную"""
        task = self.get_object()
        task.mark_completed()
        
        # Отправляем уведомление через WebSocket
        self._send_websocket_notification(task, 'task_completed')
        
        return Response({'status': 'Task marked as completed'})
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к задаче"""
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            
            # Отправляем уведомление через WebSocket
            self._send_websocket_notification(task, 'comment_added')
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Получить задачи, назначенные текущему пользователю"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        """Получить просроченные задачи"""
        now = timezone.now()
        tasks = self.get_queryset().filter(
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    def _send_websocket_notification(self, task, event_type):
        """Отправляет уведомление через WebSocket"""
        channel_layer = get_channel_layer()
        
        # Отправляем уведомление исполнителю задачи
        if task.assigned_to:
            async_to_sync(channel_layer.group_send)(
                f"user_{task.assigned_to.id}",
                {
                    'type': 'task_notification',
                    'event': event_type,
                    'task_id': task.id,
                    'task_title': task.title,
                    'message': self._get_notification_message(task, event_type)
                }
            )
        
        # Отправляем уведомление создателю задачи (если это не тот же пользователь)
        if task.created_by != task.assigned_to:
            async_to_sync(channel_layer.group_send)(
                f"user_{task.created_by.id}",
                {
                    'type': 'task_notification',
                    'event': event_type,
                    'task_id': task.id,
                    'task_title': task.title,
                    'message': self._get_notification_message(task, event_type)
                }
            )
    
    def _get_notification_message(self, task, event_type):
        """Генерирует сообщение для уведомления"""
        messages = {
            'task_created': f'Вам назначена новая задача: {task.title}',
            'task_updated': f'Задача обновлена: {task.title}',
            'task_completed': f'Задача выполнена: {task.title}',
            'comment_added': f'Добавлен комментарий к задаче: {task.title}',
        }
        return messages.get(event_type, f'Обновление задачи: {task.title}')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения информации о пользователях"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для управления профилями пользователей"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
