from django.conf import settings
from django.db import models


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField("Фото", upload_to='products/')
    is_main = models.BooleanField("Главное фото", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Фото для {self.product.name}"

    def set_order(self, new_order):
        """Устанавливает новый порядок для фотографии"""
        self.order = new_order
        self.save()

    def set_as_main(self):
        """Устанавливает текущее фото как основное"""
        # Сначала сбрасываем главное фото у всех изображений продукта
        ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        # Устанавливаем текущее фото как главное
        self.is_main = True
        self.save()


class Category(models.Model):
    name = models.CharField("Категория", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField("Бренд", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'user_type': 'seller'}
    )
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Бренд")
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        """Возвращает главное изображение товара"""
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image.image
        # Если нет главного изображения, вернем первое доступное
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None

    @property
    def additional_images(self):
        """Возвращает все дополнительные изображения товара (не главные)"""
        return self.images.filter(is_main=False)


class ProductView(models.Model):
    """Модель для отслеживания просмотров товаров пользователями"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_views',
        null=True, blank=True  # Позволяет отслеживать просмотры анонимных пользователей
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='views'
    )
    session_id = models.CharField(max_length=40, null=True, blank=True)  # Для анонимных пользователей
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Просмотр товара"
        verbose_name_plural = "Просмотры товаров"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            models.Index(fields=['product']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        user_info = self.user.email if self.user else f"Сессия {self.session_id}"
        return f"{user_info} просмотрел {self.product.name}"


class RecommendationPair(models.Model):
    """Модель для хранения пар товаров, которые часто покупают вместе"""
    product1 = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='recommendations_as_first'
    )
    product2 = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='recommendations_as_second'
    )
    score = models.FloatField(default=0.0)  # Счет релевантности (например, частота совместных покупок)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рекомендуемая пара"
        verbose_name_plural = "Рекомендуемые пары"
        unique_together = ('product1', 'product2')
        ordering = ['-score']

    def __str__(self):
        return f"{self.product1.name} → {self.product2.name} (score: {self.score})"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # чтобы не было дублей

    def __str__(self):
        return f"{self.user.email} -> {self.product.name}"

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # один товар в корзине — одна запись

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"