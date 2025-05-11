from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from accounts.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Banner
from .forms import BannerForm

from products.models import Product


def AlpamysChrot(request):
    return render(request,'AlpaChort/AlphaMath.html')
def AlpamysChortAboutUs(request):
    return render(request,'AlpaChort/aboutUs.html')
def AlpamysChortInfreg(request):
    return render(request,'AlpaChort/infRegistr.html')
def AlpamysChortMathreg(request):
    return render(request,'AlpaChort/mathRegistr.html')






# Убираем кэширование для отладки
def home(request):
    # Получаем все активные баннеры, отсортированные по порядку
    banners = Banner.objects.filter(is_active=True).order_by('order')
    
    # Получаем популярные товары (например, последние 8 активных товаров)
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    context = {
        'banners': banners,
        'products': products,
    }
    return render(request, 'html/main/home.html', context)

def about(request):
    return render(request, 'html/main/about.html')

def base(request):
    return render(request, 'html/main/base.html')



def seller_profile(request, seller_id):
    seller = CustomUser.objects.get(id=seller_id)
    product = Product.objects.filter(seller = seller)
    print(seller)
    print(product)
    return render(request, 'html/accounts/public_seller_profile.html', {'seller': seller, 'products': product})



def faq(request):
    """Страница с часто задаваемыми вопросами"""
    # Список вопросов и ответов для отображения на странице
    faq_items = [
        {
            'id': 'delivery',
            'question': 'Как происходит доставка товаров?',
            'answer': 'Доставка товаров осуществляется по всей стране. Сроки доставки зависят от региона и обычно составляют от 1 до 7 рабочих дней. Стоимость доставки рассчитывается автоматически при оформлении заказа в зависимости от веса товара и адреса доставки.'
        },
        {
            'id': 'payment',
            'question': 'Какие способы оплаты доступны?',
            'answer': 'Мы принимаем различные способы оплаты: банковские карты (Visa, MasterCard), электронные деньги, оплата через мобильный банкинг, а также наличными при получении (для доставки курьером). Выберите наиболее удобный для вас способ при оформлении заказа.'
        },
        {
            'id': 'return',
            'question': 'Как вернуть товар?',
            'answer': 'Вы можете вернуть товар в течение 14 дней с момента получения, если он не был в употреблении и сохранены его товарный вид, потребительские свойства, пломбы и фабричные ярлыки. Для возврата необходимо заполнить заявление в личном кабинете или связаться с нашей службой поддержки.'
        },
        {
            'id': 'warranty',
            'question': 'Какие гарантии предоставляются на товары?',
            'answer': 'На все товары предоставляется гарантия производителя. Срок гарантии указан в карточке товара и в сопроводительных документах. В случае обнаружения заводского брака или неисправности в течение гарантийного срока, мы производим бесплатный ремонт, замену товара или возврат денежных средств.'
        },
        {
            'id': 'order',
            'question': 'Как отследить статус заказа?',
            'answer': 'Отследить статус заказа можно в личном кабинете на сайте или через мобильное приложение. Также мы отправляем уведомления о статусе заказа на указанный при оформлении email и номер телефона. При возникновении вопросов вы всегда можете связаться с нашей службой поддержки.'
        },
        {
            'id': 'discount',
            'question': 'Есть ли система скидок или бонусная программа?',
            'answer': 'Да, у нас действует бонусная программа лояльности. За каждую покупку вы получаете бонусные баллы, которые можно использовать для оплаты последующих заказов. Также мы регулярно проводим акции и предлагаем промокоды со скидками для наших клиентов.'
        },
        {
            'id': 'wholesale',
            'question': 'Возможны ли оптовые закупки?',
            'answer': 'Да, мы работаем с оптовыми заказами. Для получения специальных условий и оптовых цен, пожалуйста, свяжитесь с нашим отделом продаж по телефону или через форму на сайте. Мы подготовим индивидуальное предложение с учетом ваших потребностей.'
        },
        {
            'id': 'international',
            'question': 'Осуществляете ли вы международную доставку?',
            'answer': 'Да, мы осуществляем доставку в страны ближнего и дальнего зарубежья. Стоимость и сроки международной доставки зависят от страны назначения. Для уточнения деталей, пожалуйста, обратитесь в нашу службу поддержки.'
        }
    ]
    
    # Категории вопросов для быстрой навигации
    faq_categories = [
        {'id': 'delivery', 'name': 'Доставка'},
        {'id': 'payment', 'name': 'Оплата'},
        {'id': 'return', 'name': 'Возврат'},
        {'id': 'warranty', 'name': 'Гарантия'},
        {'id': 'general', 'name': 'Общие вопросы'}
    ]
    
    context = {
        'faq_items': faq_items,
        'faq_categories': faq_categories
    }
    
    return render(request, 'html/main/faq.html', context)

def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def create_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, 'Баннер успешно создан')
            return redirect('banner_list')
    else:
        form = BannerForm()
    
    return render(request, 'html/banner/banner_form.html', {
        'form': form,
        'title': 'Создание баннера'
    })

@login_required
@user_passes_test(is_staff_user)
def edit_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Баннер успешно обновлен')
            return redirect('banner_list')
    else:
        form = BannerForm(instance=banner)
    
    return render(request, 'html/banner/banner_form.html', {
        'form': form,
        'banner': banner,
        'title': 'Редактирование баннера'
    })

@login_required
@user_passes_test(is_staff_user)
def banner_list(request):
    banners = Banner.objects.all()
    return render(request, 'html/banner/banner_list.html', {
        'banners': banners,
        'title': 'Управление баннерами'
    })

@login_required
@user_passes_test(is_staff_user)
def delete_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Баннер успешно удален')
        return redirect('banner_list')
    return render(request, 'html/banner_confirm_delete.html', {
        'banner': banner,
        'title': 'Удаление баннера'
    })

