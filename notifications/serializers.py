"""
Serializers for notifications.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 
            'is_read', 'created_at', 'read_at', 'task'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания уведомлений"""
    
    class Meta:
        model = Notification
        fields = ['user', 'notification_type', 'title', 'message', 'task']
