from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages

from main.models import Product
from .forms import LoginForm, RegisterForm

def auth_view(request):
    login_form = LoginForm(request, data=request.POST or None)
    register_form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            if login_form.is_valid():
                user = login_form.get_user()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request,user)
                return redirect('profile')
            else:
                messages.error(request, "Invalid email or password.")

        elif action == 'register':
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)  # Автоматический вход после регистрации
                messages.success(request, "Registration successful!")
                return redirect('profile')
            # Ошибки формы будут отображаться автоматически в шаблоне

    return render(request, 'html/accounts/login.html', {
        'login_form': login_form,
        'register_form': register_form,
    })

@login_required
def profile_view(request):
    user = request.user
    products = Product.objects.filter(seller=user)

    if user.user_type == 'seller':
        return render(request, 'html/accounts/profile_seller.html', {'user': user, 'products': products})
    else:
        return render(request, 'html/accounts/profile_customer.html', {'user': user})




def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('auth')