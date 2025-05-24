from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_order_notification(order, template_name, subject):
    """
    Отправка уведомления о заказе
    """
    try:
        # Формируем контекст для шаблона
        context = {
            'order': order,
            'user': order.user,
            'items': order.items.all(),
            'total': order.total,
            'payment_method': order.get_payment_method_display(),
            'status': order.get_status_display()
        }
        
        # Рендерим HTML-версию письма
        html_message = render_to_string(f'email/orders/{template_name}.html', context)
        
        # Рендерим текстовую версию письма
        plain_message = strip_tags(html_message)
        
        # Отправляем письмо
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Уведомление отправлено для заказа #{order.number}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")
        return False

def send_order_confirmation(order):
    """
    Отправка подтверждения заказа
    """
    return send_order_notification(
        order=order,
        template_name='order_confirmation',
        subject=f'Подтверждение заказа #{order.number}'
    )

def send_payment_confirmation(order):
    """
    Отправка подтверждения оплаты
    """
    return send_order_notification(
        order=order,
        template_name='payment_confirmation',
        subject=f'Оплата заказа #{order.number} подтверждена'
    )

def send_order_status_update(order):
    """
    Отправка уведомления об изменении статуса заказа
    """
    return send_order_notification(
        order=order,
        template_name='order_status_update',
        subject=f'Статус заказа #{order.number} обновлен'
    )

def send_payment_reminder(order):
    """
    Отправка напоминания об оплате
    """
    return send_order_notification(
        order=order,
        template_name='payment_reminder',
        subject=f'Напоминание об оплате заказа #{order.number}'
    ) 