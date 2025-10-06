"""
Telegram bot implementation using aiogram.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.contrib.auth.models import User
from tasks.models import Task, UserProfile
import requests
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Состояния пользователей
user_states = {}


def send_message_to_user(chat_id, message):
    """
    Синхронная функция для отправки сообщения пользователю
    """
    try:
        asyncio.create_task(bot.send_message(chat_id, message))
        return True
    except Exception as e:
        logger.error(f"Error sending message to {chat_id}: {str(e)}")
        return False


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    chat_id = message.chat.id
    username = message.from_user.username

    # Проверяем, зарегистрирован ли пользователь
    try:
        user_profile = UserProfile.objects.get(telegram_chat_id=chat_id)
        user = user_profile.user

        await message.answer(
            f"Привет, {user.first_name or user.username}!\n\n"
            "Я бот для управления задачами. Вот что я умею:\n"
            "/tasks - показать мои задачи\n"
            "/overdue - показать просроченные задачи\n"
            "/help - помощь"
        )
    except UserProfile.DoesNotExist:
        await message.answer(
            "Привет! Для использования бота необходимо сначала зарегистрироваться "
            "в веб-приложении и связать аккаунт с Telegram.\n\n"
            "Перейдите в настройки профиля в веб-приложении и введите этот код:\n"
            f"`{chat_id}`\n\n"
            "Или используйте команду /link для привязки аккаунта.",
            parse_mode='Markdown'
        )


@dp.message(Command("link"))
async def link_account(message: types.Message):
    """Обработчик команды /link для привязки аккаунта"""
    chat_id = message.chat.id
    username = message.from_user.username

    # Проверяем, не привязан ли уже аккаунт
    try:
        UserProfile.objects.get(telegram_chat_id=chat_id)
        await message.answer("Ваш аккаунт уже привязан к Telegram!")
        return
    except UserProfile.DoesNotExist:
        pass

    await message.answer(
        "Для привязки аккаунта введите ваш username из веб-приложения:\n\n"
        "Пример: `myusername`",
        parse_mode='Markdown'
    )
    user_states[chat_id] = 'waiting_username'


@dp.message(Command("tasks"))
async def show_tasks(message: types.Message):
    """Показать задачи пользователя"""
    chat_id = message.chat.id

    try:
        user_profile = UserProfile.objects.get(telegram_chat_id=chat_id)
        user = user_profile.user

        tasks = Task.objects.filter(
            assigned_to=user).order_by('-created_at')[:10]

        if not tasks:
            await message.answer("У вас нет назначенных задач.")
            return

        response = "📋 Ваши задачи:\n\n"
        for task in tasks:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(task.status, '❓')

            priority_emoji = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🔴'
            }.get(task.priority, '⚪')

            due_date = ""
            if task.due_date:
                due_date = f"\n📅 Срок: {task.due_date.strftime('%d.%m.%Y %H:%M')}"

            response += (
                f"{status_emoji} {priority_emoji} *{task.title}*\n"
                f"📝 {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
                f"📊 Статус: {task.get_status_display()}\n"
                f"🏷️ Приоритет: {task.get_priority_display()}{due_date}\n"
                f"👤 Создатель: {task.created_by.username}\n\n"
            )

        # Добавляем кнопки для управления задачами
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔄 Обновить", callback_data="refresh_tasks")],
            [InlineKeyboardButton(
                text="📋 Все задачи", url=f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/")]
        ])

        await message.answer(response, parse_mode='Markdown', reply_markup=keyboard)

    except UserProfile.DoesNotExist:
        await message.answer("Сначала привяжите ваш аккаунт командой /link")


@dp.message(Command("overdue"))
async def show_overdue_tasks(message: types.Message):
    """Показать просроченные задачи"""
    chat_id = message.chat.id

    try:
        user_profile = UserProfile.objects.get(telegram_chat_id=chat_id)
        user = user_profile.user

        from django.utils import timezone
        now = timezone.now()
        overdue_tasks = Task.objects.filter(
            assigned_to=user,
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')

        if not overdue_tasks:
            await message.answer("У вас нет просроченных задач! 🎉")
            return

        response = "🚨 Просроченные задачи:\n\n"
        for task in overdue_tasks:
            days_overdue = (now - task.due_date).days
            response += (
                f"⚠️ *{task.title}*\n"
                f"📅 Просрочена на {days_overdue} дн.\n"
                f"📝 {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n\n"
            )

        await message.answer(response, parse_mode='Markdown')

    except UserProfile.DoesNotExist:
        await message.answer("Сначала привяжите ваш аккаунт командой /link")


@dp.message(Command("help"))
async def help_command(message: types.Message):
    """Показать справку"""
    help_text = (
        "🤖 *Бот управления задачами*\n\n"
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/link - привязать аккаунт\n"
        "/tasks - показать мои задачи\n"
        "/overdue - показать просроченные задачи\n"
        "/help - эта справка\n\n"
        "Для полного управления задачами используйте веб-приложение."
    )
    await message.answer(help_text, parse_mode='Markdown')


@dp.callback_query(F.data == "refresh_tasks")
async def refresh_tasks_callback(callback: types.CallbackQuery):
    """Обновить список задач"""
    await callback.answer("Обновляем...")
    await show_tasks(callback.message)


@dp.message()
async def handle_text_message(message: types.Message):
    """Обработчик текстовых сообщений"""
    chat_id = message.chat.id
    text = message.text

    if chat_id in user_states and user_states[chat_id] == 'waiting_username':
        # Пользователь вводит username для привязки
        username = text.strip()

        try:
            user = User.objects.get(username=username)
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'telegram_chat_id': chat_id,
                          'telegram_username': message.from_user.username}
            )

            if not created:
                user_profile.telegram_chat_id = chat_id
                user_profile.telegram_username = message.from_user.username
                user_profile.save()

            del user_states[chat_id]
            await message.answer(
                f"✅ Аккаунт успешно привязан!\n\n"
                f"Добро пожаловать, {user.first_name or user.username}!\n"
                f"Теперь вы можете использовать команду /tasks для просмотра ваших задач."
            )

        except User.DoesNotExist:
            await message.answer(
                f"❌ Пользователь с именем '{username}' не найден.\n"
                f"Проверьте правильность написания и попробуйте снова."
            )
    else:
        await message.answer(
            "Не понимаю эту команду. Используйте /help для просмотра доступных команд."
        )


async def start_bot():
    """Запуск бота"""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")


def run_bot():
    """Синхронная функция для запуска бота"""
    asyncio.run(start_bot())
