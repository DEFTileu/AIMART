from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages

from products.models import Product, Category, Brand
from .forms import LoginForm, RegisterForm
from .models import Card

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def auth_view(request):
    login_form = LoginForm(request, data=request.POST or None)
    register_form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            if login_form.is_valid():
                email = login_form.cleaned_data.get('username')  # или .get('email'), если форма так названа
                password = login_form.cleaned_data.get('password')

                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)  # backend будет установлен автоматически
                    return redirect('profile')
                else:
                    messages.error(request, "Authentication failed.")
            else:
                messages.error(request, "Invalid email or password.")

        elif action == 'register':
            if register_form.is_valid():
                user = register_form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # явно укажем backend
                messages.success(request, "Registration successful!")
                return redirect('profile')

    return render(request, 'html/accounts/login.html', {
        'login_form': login_form,
        'register_form': register_form,
    })


@login_required
def profile_view(request):
    user = request.user
    
    # Обработка запроса на обновление профиля
    if request.method == 'POST' and request.POST.get('action') == 'update_profile':
        # Обновление имени пользователя
        if 'full_name' in request.POST:
            user.full_name = request.POST.get('full_name')
        
        # Обработка фотографий профиля
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')
        elif request.POST.get('remove_avatar'):
            user.avatar = None
            
        # Обработка дополнительных фотографий
        for i in range(2, 6):
            field_name = f'avatar_{i}'
            if request.FILES.get(field_name):
                setattr(user, field_name, request.FILES.get(field_name))
            elif request.POST.get(f'remove_{field_name}'):
                setattr(user, field_name, None)
                
        user.save()
        messages.success(request, "Профиль успешно обновлен!")
        return redirect('profile')

    if user.user_type == 'seller':
        products = Product.objects.filter(seller=user)
        products_count = products.count()
        active_products_count = products.filter(is_active=True).count()
        categories = Category.objects.all()
        brands = Brand.objects.all()
        return render(request, 'html/accounts/profile_seller.html', {
            'user': user, 
            'products': products,
            'products_count': products_count,
            'active_products_count': active_products_count,
            'categories': categories,
            'brands':brands
        })
    else:
        return render(request, 'html/accounts/profile_customer.html', {'user': user})




def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('auth')

# @login_required
# def card_list(request):
#     cards = Card.objects.filter(user=request.user)
#     form = CardForm()
#
#     if request.method == 'POST':
#         form = CardForm(request.POST)
#         if form.is_valid():
#             card = form.save(commit=False)
#             card.user = request.user
#             card.save()
#             messages.success(request, 'Карта успешно добавлена')
#             return redirect('card_list')
#
#     return render(request, 'accounts/card_list.html', {
#         'cards': cards,
#         'form': form
#     })
#
# @login_required
# def delete_card(request, card_id):
#     try:
#         card = Card.objects.get(id=card_id, user=request.user)
#         card.delete()
#         messages.success(request, 'Карта успешно удалена')
#     except Card.DoesNotExist:
#         messages.error(request, 'Карта не найдена')
#     return redirect('card_list')
#
# @login_required
# def set_default_card(request, card_id):
#     try:
#         # Сбрасываем все карты как не дефолтные
#         Card.objects.filter(user=request.user).update(is_default=False)
#         # Устанавливаем выбранную карту как дефолтную
#         card = Card.objects.get(id=card_id, user=request.user)
#         card.is_default = True
#         card.save()
#         messages.success(request, 'Карта установлена как основная')
#     except Card.DoesNotExist:
#         messages.error(request, 'Карта не найдена')
#     return redirect('card_list')