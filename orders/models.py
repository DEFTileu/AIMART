import uuid
from datetime import datetime
import random

from accounts.models import CustomUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from products.models import Product

User = get_user_model()

class Order(models.Model):
    PAYMENT_METHODS = (
        ('CARD', 'Банковская карта'),
        ('KASPI', 'Kaspi'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('failed', 'Ошибка оплаты'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    number = models.CharField(max_length=20, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = get_random_string(10).upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Заказ #{self.number}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    class Meta:
        ordering = ['id']

class SavedCard(models.Model):
    CARD_TYPES = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMEX', 'American Express'),
        ('MAESTRO', 'Maestro'),
        ('MIR', 'MIR'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_cards')
    card_type = models.CharField(max_length=10, choices=CARD_TYPES)
    last_four = models.CharField(max_length=4)
    expiry_month = models.PositiveIntegerField()
    expiry_year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_card_type_display()} **** {self.last_four}"
    
    class Meta:
        ordering = ['-created_at']