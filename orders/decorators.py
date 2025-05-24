from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import Order
from .constants import ORDER_STATUS, ERROR_MESSAGES

def require_active_order(view_func):
    """
    Декоратор для проверки наличия активного заказа
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'order_id' not in request.session:
            messages.error(request, ERROR_MESSAGES['ORDER_NOT_FOUND'])
            return redirect(reverse('checkout'))
        
        try:
            order = Order.objects.get(id=request.session['order_id'])
            if order.status != ORDER_STATUS['PENDING']:
                del request.session['order_id']
                messages.error(request, ERROR_MESSAGES['INVALID_ORDER_STATUS'])
                return redirect(reverse('checkout'))
        except Order.DoesNotExist:
            del request.session['order_id']
            messages.error(request, ERROR_MESSAGES['ORDER_NOT_FOUND'])
            return redirect(reverse('checkout'))
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def require_paid_order(view_func):
    """
    Декоратор для проверки оплаты заказа
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'order_id' not in request.session:
            messages.error(request, ERROR_MESSAGES['ORDER_NOT_FOUND'])
            return redirect(reverse('checkout'))
        
        try:
            order = Order.objects.get(id=request.session['order_id'])
            if order.status != ORDER_STATUS['PAID']:
                messages.error(request, ERROR_MESSAGES['INVALID_ORDER_STATUS'])
                return redirect(reverse('checkout'))
        except Order.DoesNotExist:
            del request.session['order_id']
            messages.error(request, ERROR_MESSAGES['ORDER_NOT_FOUND'])
            return redirect(reverse('checkout'))
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view 