from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Отправляет уведомление при изменении статуса заказа
    """
    if not created and instance.status == 'paid':
        # Отправляем уведомление об успешной оплате
        subject = f'Заказ #{instance.number} успешно оплачен'
        message = f'''
        Здравствуйте!
        
        Ваш заказ #{instance.number} успешно оплачен.
        
        Сумма заказа: {instance.total} ₸
        Способ оплаты: {instance.get_payment_method_display()}
        
        Спасибо за покупку!
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=True
        ) 