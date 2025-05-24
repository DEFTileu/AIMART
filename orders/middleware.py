from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Order
from .constants import ORDER_STATUS

class OrderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, есть ли активный заказ в сессии
        if 'order_id' in request.session:
            try:
                order = Order.objects.get(id=request.session['order_id'])
                
                # Если заказ уже оплачен, удаляем его из сессии
                if order.status == ORDER_STATUS['PAID']:
                    del request.session['order_id']
                
                # Если заказ отменен или произошла ошибка, удаляем его из сессии
                elif order.status in [ORDER_STATUS['CANCELLED'], ORDER_STATUS['FAILED']]:
                    del request.session['order_id']
                    messages.error(request, 'Заказ был отменен или произошла ошибка при оплате')
            
            except Order.DoesNotExist:
                # Если заказ не найден, удаляем его из сессии
                del request.session['order_id']
        
        response = self.get_response(request)
        return response 