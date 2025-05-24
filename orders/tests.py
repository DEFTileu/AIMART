from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from .models import Order, OrderItem, SavedCard
from decimal import Decimal

User = get_user_model()

class OrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('1000.00'),
            description='Test Description'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_order(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            user=self.user,
            total=Decimal('1000.00'),
            payment_method='CARD'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1
        )
        
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total, Decimal('1000.00'))
        self.assertEqual(order.items.count(), 1)
    
    def test_checkout_page(self):
        """Тест страницы оформления заказа"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/orders/checkout.html')
    
    def test_waiting_page(self):
        """Тест страницы ожидания оплаты"""
        order = Order.objects.create(
            user=self.user,
            total=Decimal('1000.00'),
            payment_method='CARD'
        )
        response = self.client.get(reverse('waiting', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/orders/waiting.html')
    
    def test_kaspi_qr_page(self):
        """Тест страницы с QR-кодом Kaspi"""
        order = Order.objects.create(
            user=self.user,
            total=Decimal('1000.00'),
            payment_method='KASPI'
        )
        response = self.client.get(reverse('kaspi_qr', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/orders/kaspi_qr.html')
    
    def test_success_page(self):
        """Тест страницы успешной оплаты"""
        order = Order.objects.create(
            user=self.user,
            total=Decimal('1000.00'),
            payment_method='CARD',
            status='paid'
        )
        response = self.client.get(reverse('success', args=[order.number]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/orders/success.html')
    
    def test_save_card(self):
        """Тест сохранения карты"""
        card = SavedCard.objects.create(
            user=self.user,
            card_type='VISA',
            last_four='1234',
            expiry_month=12,
            expiry_year=2025
        )
        self.assertEqual(card.user, self.user)
        self.assertEqual(card.card_type, 'VISA')
        self.assertEqual(card.last_four, '1234')
