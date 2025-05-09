from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator

from .forms import NewsForm
from .models import News


# Create your views here.
# Представления для новостей
@cache_page(60 * 30)  # Кэширование на 30 минут
def news_list(request):
    """Страница со списком новостей"""
    # Проверяем кэш
    cache_key = f'news_list_page_{request.GET.get("page", 1)}'
    cached_context = cache.get(cache_key)

    if cached_context:
        return render(request, 'html/news/news_list.html', cached_context)

    news = News.objects.filter(is_published=True).select_related()


    # Пагинация
    paginator = Paginator(news, 6)  # 6 новостей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'news_list': page_obj.object_list,
        'paginator': paginator
    }

    # Кэшируем контекст
    cache.set(cache_key, context, 60 * 15)  # 15 минут

    return render(request, 'html/news/news_list.html', context)


def news_detail(request, slug):
    """Страница с детальной информацией о новости"""
    # Попытка получения из кэша
    cache_key = f'news_detail_{slug}'
    cached_data = cache.get(cache_key)

    if cached_data:
        news_item, other_news = cached_data
    else:
        news_item = get_object_or_404(News, slug=slug, is_published=True)
        # Получаем другие новости для секции "Другие новости"
        other_news = News.objects.filter(is_published=True).exclude(id=news_item.id)[:3]

        # Кэшируем данные на 30 минут
        cache.set(cache_key, (news_item, other_news), 60 * 30)

    # Увеличиваем счетчик просмотров
    try:
        news_item.increment_views()
    except Exception as e:
        print(f"Ошибка при увеличении счётчика просмотров: {e}")

    context = {
        'news_item': news_item,
        'other_news': other_news
    }
    return render(request, 'html/news/news_detail.html', context)


@login_required
def add_news(request):
    """Представление для добавления новой новости"""

    # Проверка прав доступа (опционально - если нужно ограничить создание новостей)
    # if hasattr(request.user, 'user_type'):
    # # if hasattr(request.user, 'user_type') and request.user.user_type != 'admin':
    #     messages.error(request, "У вас нет прав для создания новостей")
    #     return redirect('news_list')

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Сохраняем новость (slug генерируется автоматически в форме)
                news = form.save()

                messages.success(request, "Новость успешно создана!")
                return redirect('news_detail', slug=news.slug)
            except Exception as e:
                messages.error(request, f"Ошибка при создании новости: {e}")
        else:
            # Если форма не валидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле '{form.fields[field].label}': {error}")
    else:
        # GET запрос - показываем пустую форму
        form = NewsForm()

    return render(request, 'html/news/add_news.html', {
        'form': form,
        'is_edit': False,
        'title': 'Создание новости'
    })


@login_required
def edit_news(request, slug):
    """Представление для редактирования существующей новости"""

    # Получаем новость или возвращаем 404
    news_item = get_object_or_404(News, slug=slug)

    # Проверка прав доступа (опционально - если нужно ограничить редактирование)
    if hasattr(request.user, 'user_type') and request.user.user_type != 'admin':
        messages.error(request, "У вас нет прав для редактирования новостей")
        return redirect('news_detail', slug=slug)

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            try:
                # Сохраняем новость (slug обновляется автоматически)
                news = form.save()

                messages.success(request, "Новость успешно обновлена!")
                return redirect('news_detail', slug=news.slug)
            except Exception as e:
                messages.error(request, f"Ошибка при обновлении новости: {e}")
        else:
            # Если форма не валидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле '{form.fields[field].label}': {error}")
    else:
        # GET запрос - показываем форму с данными новости
        form = NewsForm(instance=news_item)

    return render(request, 'html/news/add_news.html', {
        'form': form,
        'is_edit': True,
        'title': f'Редактирование новости "{news_item.title}"'
    })
