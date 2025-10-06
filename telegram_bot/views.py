"""
Views for telegram bot.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    """
    Webhook для получения обновлений от Telegram
    """
    try:
        update_data = json.loads(request.body)
        logger.info(f"Received update: {update_data}")
        
        # Здесь можно добавить обработку webhook'ов
        # В текущей реализации используется polling
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
