class OrderError(Exception):
    """Базовый класс для исключений заказов"""
    pass

class InvalidOrderError(OrderError):
    """Исключение при неверных данных заказа"""
    pass

class PaymentError(OrderError):
    """Исключение при ошибке оплаты"""
    pass

class InvalidCardError(OrderError):
    """Исключение при неверных данных карты"""
    pass

class OrderNotFoundError(OrderError):
    """Исключение при отсутствии заказа"""
    pass

class InvalidOrderStatusError(OrderError):
    """Исключение при недопустимом статусе заказа"""
    pass

class InvalidPaymentMethodError(OrderError):
    """Исключение при недопустимом способе оплаты"""
    pass 