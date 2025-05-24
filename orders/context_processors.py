from .models import Order
from .constants import ORDER_STATUS

def active_order(request):
    """
    Добавляет информацию об активном заказе в контекст шаблона
    """
    context = {
        'active_order': None,
        'order_status': None
    }
    
    if 'order_id' in request.session:
        try:
            order = Order.objects.get(id=request.session['order_id'])
            context['active_order'] = order
            context['order_status'] = order.status
        except Order.DoesNotExist:
            del request.session['order_id']
    
    return context

def order_statuses(request):
    """
    Добавляет статусы заказов в контекст шаблона
    """
    return {
        'ORDER_STATUS': ORDER_STATUS
    } 