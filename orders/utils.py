import qrcode
import base64
from io import BytesIO
from django.conf import settings
from datetime import datetime

def detect_card_type(card_number):
    if card_number.startswith('4'):
        return 'VISA'
    elif card_number.startswith('5'):
        return 'MASTERCARD'
    elif card_number.startswith(('34', '37')):
        return 'AMEX'
    elif card_number.startswith(('50', '56', '57', '58', '6')):
        return 'MAESTRO'
    elif card_number.startswith('2200') or card_number.startswith('2204'):
        return 'MIR'
    return 'UNKNOWN'

def generate_kaspi_qr(order_number, amount):
    """
    Генерирует QR-код для оплаты через Kaspi
    """
    # Формируем данные для QR-кода
    qr_data = {
        'order_number': order_number,
        'amount': str(amount),
        'timestamp': datetime.now().strftime('%Y%m%d%H%M%S'),
        'merchant_id': settings.KASPI_MERCHANT_ID
    }
    
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(qr_data))
    qr.make(fit=True)
    
    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Конвертируем в base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def process_card_payment(card_number, expiry_month, expiry_year, cvv, amount):
    """
    Обрабатывает платеж по карте
    В реальном приложении здесь должна быть интеграция с платежной системой
    """
    # Здесь должна быть реальная интеграция с платежной системой
    # Для демонстрации просто возвращаем успешный результат
    return {
        'success': True,
        'transaction_id': f"TRANS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'status': 'success'
    }

def check_payment_status(order):
    """
    Проверяет статус платежа
    В реальном приложении здесь должна быть интеграция с платежной системой
    """
    # Здесь должна быть реальная интеграция с платежной системой
    # Для демонстрации просто возвращаем статус из модели
    return {
        'status': order.status,
        'paid': order.status == 'paid'
    }

def check_kaspi_payment(order):
    """
    Проверяет статус платежа через Kaspi
    В реальном приложении здесь должна быть интеграция с Kaspi
    """
    # Здесь должна быть реальная интеграция с Kaspi
    # Для демонстрации просто возвращаем статус из модели
    return {
        'status': order.status,
        'paid': order.status == 'paid'
    }
