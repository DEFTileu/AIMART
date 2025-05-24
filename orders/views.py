from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .forms import OrderForm, CardForm, PaymentForm, CardPaymentForm
from .models import Order, OrderItem, SavedCard
from accounts.models import Card
from products.models import Product, CartItem
from django.utils import timezone
import json
import qrcode
import io
import base64
from .utils import generate_kaspi_qr, process_card_payment, check_payment_status, check_kaspi_payment
from .decorators import require_active_order, require_paid_order
from .constants import ORDER_STATUS, ERROR_MESSAGES, SUCCESS_MESSAGES
from django.urls import reverse
from decimal import Decimal

# Create your views here.

@login_required
def checkout(request):
    """
    Представление для страницы оформления заказа
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            save_card = form.cleaned_data.get('save_card', False)
            
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                total=Decimal(request.session.get('cart_total', 0)),
                payment_method=payment_method
            )
            
            # Добавляем товары в заказ
            cart_items = request.session.get('cart', {})
            for product_id, quantity in cart_items.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )
            
            # Сохраняем ID заказа в сессии
            request.session['order_id'] = order.id
            
            # Перенаправляем на соответствующую страницу в зависимости от способа оплаты
            if payment_method == 'KASPI':
                return redirect('orders:kaspi_qr', order_id=order.id)
            else:
                return redirect('orders:waiting', order_id=order.id)
    else:
        form = PaymentForm()
    
    # Получаем товары из корзины
    cart_items = []
    total = Decimal('0.00')
    cart = request.session.get('cart', {})
    
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    # Сохраняем общую сумму в сессии
    request.session['cart_total'] = str(total)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'html/orders/checkout.html', context)

@login_required
@require_active_order
def waiting(request, order_id):
    """
    Представление для страницы ожидания оплаты
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'html/orders/waiting.html', context)

@login_required
@require_active_order
def kaspi_qr(request, order_id):
    """
    Представление для страницы с QR-кодом Kaspi
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Генерируем QR-код
    qr_code = generate_kaspi_qr(order.number, order.total)
    
    context = {
        'order': order,
        'qr_code': qr_code
    }
    
    return render(request, 'html/orders/kaspi_qr.html', context)

@login_required
@require_paid_order
def success(request, order_number):
    """
    Представление для страницы успешной оплаты
    """
    order = get_object_or_404(Order, number=order_number, user=request.user)
    
    # Очищаем корзину
    if 'cart' in request.session:
        del request.session['cart']
    if 'cart_total' in request.session:
        del request.session['cart_total']
    if 'order_id' in request.session:
        del request.session['order_id']
    
    context = {
        'order': order
    }
    
    return render(request, 'html/orders/success.html', context)

@login_required
@require_active_order
def check_status(request, order_id):
    """
    Представление для проверки статуса оплаты
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Проверяем статус оплаты
    status = check_payment_status(order)
    
    if status['paid']:
        # Обновляем статус заказа
        order.status = ORDER_STATUS['PAID']
        order.paid_at = timezone.now()
        order.save()
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('orders:success', args=[order.number])
        })
    
    return JsonResponse({
        'status': 'pending'
    })

@login_required
@require_active_order
def check_kaspi_status(request, order_id):
    """
    Представление для проверки статуса оплаты через Kaspi
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Проверяем статус оплаты
    status = check_kaspi_payment(order)
    
    if status['paid']:
        # Обновляем статус заказа
        order.status = ORDER_STATUS['PAID']
        order.paid_at = timezone.now()
        order.save()
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('orders:success', args=[order.number])
        })
    
    return JsonResponse({
        'status': 'pending'
    })

@login_required
def get_saved_cards(request):
    """
    Представление для получения сохраненных карт пользователя
    """
    cards = SavedCard.objects.filter(user=request.user)
    
    return JsonResponse({
        'cards': [
            {
                'id': card.id,
                'card_type': card.card_type,
                'last_four': card.last_four,
                'expiry_month': card.expiry_month,
                'expiry_year': card.expiry_year
            }
            for card in cards
        ]
    })
