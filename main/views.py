from itertools import product

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import CustomUser


def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'html/home.html',{'products':products})

def about(request):
    return render(request, 'html/about.html')

def base(request):
    return render(request, 'html/base.html')

def catalog(request):
    return render(request, 'html/catalog.html')

def favorites(request):
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user)
        return render(request, 'html/favorites.html', {'favorites': user_favorites})
    else:
        return render(request, 'html/favorites.html', {'favorites': []})

def cart(request):
    return render(request, 'html/cart.html')

def login(request):
    return render(request, 'html/accounts/login.html')


from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Product

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.seller = request.user  # Привязываем товар к текущему пользователю
                product.save()  # Сохраняем товар
                return redirect('profile')  # Перенаправление на страницу профиля
            except Exception as e:
                print(f"Ошибка при сохранении товара: {e}")
                return render(request, 'html/accounts/profile_seller.html', {'form': form, 'error': 'Ошибка при сохранении товара'})
        else:
            print(f"Форма невалидна: {form.errors}")
            return render(request, 'html/accounts/profile_seller.html', {'form': form, 'error': 'Неверные данные формы'})
    else:
        form = ProductForm()

    return render(request, 'html/accounts/profile_seller.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from .models import Product  # модель товара, если еще не создана

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'html/product_detail.html', {'product': product})

from django.http import JsonResponse
from django.shortcuts import redirect

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    # Проверка, есть ли корзина в сессии
    cart = request.session.get('cart', [])
    cart.append(product.id)
    request.session['cart'] = cart

    return redirect('product_detail', id=id)  # возвращаем на страницу товара

def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    # Проверка, есть ли избранное в сессии
    wishlist = request.session.get('wishlist', [])
    wishlist.append(product.id)
    request.session['wishlist'] = wishlist

    return redirect('product_detail', id=id)  # возвращаем на страницу товара

def cart_view(request):
    cart = request.session.get('cart', [])
    products_in_cart = Product.objects.filter(id__in=cart)
    return render(request, 'html/cart.html', {'products': products_in_cart})

def wishlist_view(request):
    wishlist = request.session.get('wishlist', [])
    products_in_wishlist = Product.objects.filter(id__in=wishlist)
    return render(request, 'html/favorites.html', {'products': products_in_wishlist})

def seller_profile(request, seller_id):
    seller = CustomUser.objects.get(id=seller_id)
    product = Product.objects.filter(seller = seller)
    return render(request, 'html/accounts/public_seller_profile.html', {'seller': seller, 'products': product})

# views.py
from django.http import JsonResponse
import json
from .models import Favorite
from .models import Product

def toggle_favorite(request):
    if request.user.is_authenticated and request.method == "POST":
        try:
            # Получаем данные из JSON в теле запроса
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
                
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Product not found'})

            # Проверяем, есть ли товар в избранном
            favorite = Favorite.objects.filter(user=request.user, product=product)
            
            if favorite.exists():
                # Если товар уже в избранном - удаляем его
                favorite.delete()
                added = False
            else:
                # Если товара нет в избранном - добавляем его
                Favorite.objects.create(user=request.user, product=product)
                added = True

            # Обновляем количество избранных
            favorites_count = Favorite.objects.filter(user=request.user).count()

            return JsonResponse({
                'success': True,
                'added': added,
                'favorites_count': favorites_count,
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'User not authenticated'})


# views.py
def product_list(request):
    products = Product.objects.all()
    favorites = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'product_list.html', {
        'products': products,
        'favorites': favorites,
    })
