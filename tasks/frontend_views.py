"""
Frontend views for task management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json


def index(request):
    """Главная страница приложения"""
    if request.user.is_authenticated:
        return render(request, 'tasks/index.html')
    else:
        return render(request, 'tasks/welcome.html')


def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверные учетные данные')
    return render(request, 'tasks/login.html')


def register_view(request):
    """Страница регистрации"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')


@method_decorator(csrf_exempt, name='dispatch')
class WebSocketTokenView(View):
    """API endpoint для получения токена WebSocket"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # В реальном приложении здесь должна быть более сложная логика генерации токена
        token = f"ws_token_{request.user.id}_{request.user.username}"
        return JsonResponse({'token': token})
