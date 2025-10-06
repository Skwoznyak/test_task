"""
Serializers for task management API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import TaskList, Task, TaskComment, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'telegram_chat_id', 'telegram_username', 'phone_number', 'avatar']
        read_only_fields = ['id']


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка задач"""
    created_by = UserSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskList
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'updated_at', 'task_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к задачам"""
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач"""
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    task_list = TaskListSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'task_list', 'assigned_to', 'created_by',
            'priority', 'status', 'due_date', 'created_at', 'updated_at',
            'completed_at', 'is_overdue', 'comments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class TaskCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания задач"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_list', 'assigned_to', 'priority', 'due_date']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления задач"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'status', 'due_date']
    
    def update(self, instance, validated_data):
        # Если задача отмечается как выполненная, устанавливаем дату завершения
        if validated_data.get('status') == 'completed' and instance.status != 'completed':
            instance.completed_at = timezone.now()
        return super().update(instance, validated_data)
