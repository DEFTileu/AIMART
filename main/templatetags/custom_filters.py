from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def map_attr(object_list, attribute):
    """
    Возвращает список значений указанного атрибута из списка объектов
    Используется для получения списка продуктов из списка избранных товаров
    Пример: {{ favorites|map_attr:"product" }}
    """
    if not object_list:
        return []
    
    result = []
    for obj in object_list:
        try:
            # Поддержка вложенных атрибутов (например, "product.name")
            attrs = attribute.split('.')
            value = obj
            for attr in attrs:
                value = getattr(value, attr)
            result.append(value)
        except (AttributeError, TypeError):
            # Если атрибут не существует, пропускаем объект
            continue
    
    return result

@register.filter
def in_favorites(product_id, user):
    """
    Проверяет, находится ли продукт в избранном у пользователя
    Пример: {{ product.id|in_favorites:request.user }}
    """
    if not user.is_authenticated:
        return False
    
    # Импортируем модель внутри функции, чтобы избежать циклических импортов
    from main.models import Favorite
    
    return Favorite.objects.filter(user=user, product_id=product_id).exists()

@register.filter
def format_price(value):
    """
    Форматирует цену с разделителями тысяч
    Пример: {{ product.price|format_price }}
    """
    try:
        return '{:,}'.format(int(value)).replace(',', ' ')
    except (ValueError, TypeError):
        return value 