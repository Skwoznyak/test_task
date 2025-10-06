"""
Custom permissions for task management.
"""
from rest_framework import permissions


class IsOwnerOrAssigned(permissions.BasePermission):
    """
    Разрешение для доступа к задачам только создателю или исполнителю.
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ создателю или исполнителю задачи
        return obj.created_by == request.user or obj.assigned_to == request.user
