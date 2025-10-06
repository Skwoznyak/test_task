"""
WebSocket consumers for real-time updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Task


class TaskConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer для уведомлений о задачах"""
    
    async def connect(self):
        """Подключение к WebSocket"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Присоединяемся к группе пользователя
        self.room_group_name = f"user_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Отключение от WebSocket"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            elif message_type == 'get_tasks':
                tasks = await self.get_user_tasks()
                await self.send(text_data=json.dumps({
                    'type': 'tasks_data',
                    'tasks': tasks
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def task_notification(self, event):
        """Отправка уведомления о задаче"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'event': event['event'],
            'task_id': event['task_id'],
            'task_title': event['task_title'],
            'message': event['message']
        }))
    
    @database_sync_to_async
    def get_user_tasks(self):
        """Получение задач пользователя"""
        tasks = Task.objects.filter(
            assigned_to=self.user
        ).select_related('assigned_to', 'created_by', 'task_list')
        
        return [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat(),
                'is_overdue': task.is_overdue(),
                'task_list': {
                    'id': task.task_list.id,
                    'name': task.task_list.name
                },
                'created_by': {
                    'id': task.created_by.id,
                    'username': task.created_by.username
                }
            }
            for task in tasks
        ]
