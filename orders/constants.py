# Статусы заказа
ORDER_STATUS = {
    'PENDING': 'pending',
    'PAID': 'paid',
    'CANCELLED': 'cancelled',
    'FAILED': 'failed'
}

# Способы оплаты
PAYMENT_METHODS = {
    'CARD': 'CARD',
    'KASPI': 'KASPI'
}

# Типы карт
CARD_TYPES = {
    'VISA': 'VISA',
    'MASTERCARD': 'MASTERCARD',
    'AMEX': 'AMEX',
    'MAESTRO': 'MAESTRO',
    'MIR': 'MIR'
}

# Сообщения об ошибках
ERROR_MESSAGES = {
    'INVALID_CARD': 'Неверный номер карты',
    'INVALID_CVV': 'Неверный CVV код',
    'INVALID_EXPIRY': 'Неверная дата окончания срока действия карты',
    'PAYMENT_FAILED': 'Ошибка при обработке платежа',
    'ORDER_NOT_FOUND': 'Заказ не найден',
    'INVALID_ORDER_STATUS': 'Недопустимый статус заказа',
    'INVALID_PAYMENT_METHOD': 'Недопустимый способ оплаты'
}

# Сообщения об успехе
SUCCESS_MESSAGES = {
    'PAYMENT_SUCCESS': 'Оплата успешно произведена',
    'CARD_SAVED': 'Карта успешно сохранена',
    'ORDER_CREATED': 'Заказ успешно создан'
} 