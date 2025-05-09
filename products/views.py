import json
from itertools import combinations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count,Max,F,Q
from django.http import JsonResponse
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import ProductForm
from .models import Product, Favorite, CartItem, ProductView, Category, Brand, RecommendationPair, ProductImage


def catalog(request):
    # Базовый QuerySet всех активных товаров
    products_qs = Product.objects.filter(is_active=True).select_related('category', 'brand')

    # Получаем все категории и бренды для фильтров с использованием кэша
    cache_key_categories = 'all_categories'
    categories = cache.get(cache_key_categories)
    if not categories:
        categories = Category.objects.all()
        cache.set(cache_key_categories, categories, 60 * 60)  # Кэшируем на 1 час

    cache_key_brands = 'all_brands'
    brands = cache.get(cache_key_brands)
    if not brands:
        brands = Brand.objects.all()
        cache.set(cache_key_brands, brands, 60 * 60)  # Кэшируем на 1 час

    # Значения фильтров по умолчанию
    selected_category = None
    selected_brand = None
    min_price = None
    max_price = None
    sort_by = request.GET.get('sort', 'popular')  # По умолчанию сортировка по популярности

    # Создаем фильтр запросов
    filter_kwargs = {}

    # Применяем фильтр по категории
    if request.GET.get('category'):
        try:
            selected_category = int(request.GET.get('category'))
            filter_kwargs['category_id'] = selected_category
        except (ValueError, TypeError):
            pass

    # Применяем фильтр по бренду
    if request.GET.get('brand'):
        try:
            selected_brand = int(request.GET.get('brand'))
            filter_kwargs['brand_id'] = selected_brand
        except (ValueError, TypeError):
            pass

    # Применяем фильтр по цене (минимальная)
    if request.GET.get('min_price'):
        try:
            min_price = float(request.GET.get('min_price'))
            filter_kwargs['price__gte'] = min_price
        except (ValueError, TypeError):
            min_price = None

    # Применяем фильтр по цене (максимальная)
    if request.GET.get('max_price'):
        try:
            max_price = float(request.GET.get('max_price'))
            filter_kwargs['price__lte'] = max_price
        except (ValueError, TypeError):
            max_price = None

    # Применяем все фильтры сразу для оптимизации запросов
    if filter_kwargs:
        products_qs = products_qs.filter(**filter_kwargs)

    # Применяем сортировку
    if sort_by == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort_by == 'price_desc':
        products_qs = products_qs.order_by('-price')
    elif sort_by == 'new':
        products_qs = products_qs.order_by('-created_at')
    else:  # 'popular' или другие варианты - сортируем по популярности на основе просмотров
        # Используем аннотацию для подсчета просмотров и совместных покупок
        from django.db.models import Count, F

        # Более сложная и точная сортировка по популярности
        products_qs = products_qs.annotate(
            view_count=Count('views'),
            # Добавляем вес для рекомендаций
            rec_count1=Count('recommendations_as_first'),
            rec_count2=Count('recommendations_as_second'),
            # Считаем общую популярность как взвешенную сумму показателей
            popularity=F('view_count') + (F('rec_count1') + F('rec_count2')) * 2
        ).order_by('-popularity')

    # Пагинация результатов
    paginator = Paginator(products_qs, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj
    }

    return render(request, 'html/catalog.html', context)


def favorites(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
    else:
        wishlist = request.session.get('wishlist', [])
        favorites = []

        for product_id in wishlist:
            try:
                product = Product.objects.get(id=product_id)
                favorites.append({'product': product})
            except Product.DoesNotExist:
                pass

    return render(request, 'html/favorites.html', {'favorites': favorites})


def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    if request.user.is_authenticated:
        # Для авторизованных пользователей используем модель CartItem
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )

        # Если товар уже был в корзине, увеличиваем количество
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Обновляем рекомендации на основе корзины этого пользователя
        update_recommendations(user=request.user)
    else:
        # Для анонимных пользователей используем сессию
        cart = request.session.get('cart', [])
        cart.append(product.id)
        request.session['cart'] = cart

    return redirect('product_detail', id=id)


def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    if request.user.is_authenticated:
        # Для авторизованных пользователей используем модель Favorite
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        # Если не создан новый объект, значит запись уже существовала,
        # поэтому удаляем ее (тогглинг избранного)
        if not created:
            favorite.delete()
    else:
        # Для анонимных пользователей используем сессию
        wishlist = request.session.get('wishlist', [])

        if product.id in wishlist:
            wishlist.remove(product.id)
        else:
            wishlist.append(product.id)

        request.session['wishlist'] = wishlist

    return redirect('product_detail', id=id)


def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', [])
        # Удаляем дубликаты
        cart = list(set(cart))
        cart_items = []
        cart_total = 0

        for product_id in cart:
            try:
                product = Product.objects.get(id=product_id)
                cart_items.append({'product': product, 'quantity': 1})
                cart_total += product.price
            except Product.DoesNotExist:
                pass

    return render(request, 'html/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


def wishlist_view(request):
    wishlist = request.session.get('wishlist', [])
    products_in_wishlist = Product.objects.filter(id__in=wishlist)
    return render(request, 'html/favorites.html', {'products': products_in_wishlist})


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


# AJAX-обработчик для корзины
def cart_ajax(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            operation = data.get('operation', 'add')  # add, update, remove

            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Product not found'})

            if operation == 'add':
                # Добавляем или увеличиваем количество
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )

                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()

            elif operation == 'update':
                # Обновляем количество
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )

                if not created:
                    cart_item.quantity = quantity
                    cart_item.save()

            elif operation == 'remove':
                # Удаляем товар из корзины
                CartItem.objects.filter(user=request.user, product=product).delete()

            # Обновляем информацию о корзине
            cart_count = CartItem.objects.filter(user=request.user).count()
            cart_items = CartItem.objects.filter(user=request.user)
            cart_total = sum(item.product.price * item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'cart_total': float(cart_total)
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Обновление количества товара в корзине
def update_cart(request, id):
    product = get_object_or_404(Product, id=id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1

    if request.user.is_authenticated:
        # Для авторизованных пользователей
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity = quantity
            cart_item.save()

        # Обновляем рекомендации на основе корзины
        update_recommendations(user=request.user)

        # Возвращаем JSON с информацией о корзине
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
        cart_count = sum(item.quantity for item in cart_items)

        response_data = {
            'success': True,
            'cart_total': float(cart_total),
            'cart_count': cart_count,
            'quantity': quantity
        }
    else:
        # Для неавторизованных пользователей
        cart = request.session.get('cart', [])

        # Удаляем старые экземпляры товара
        cart = [product_id for product_id in cart if product_id != product.id]

        # Добавляем товар нужное количество раз
        for _ in range(quantity):
            cart.append(product.id)

        request.session['cart'] = cart

        # Рассчитываем итоги для сессионной корзины
        cart_items = []
        cart_total = 0

        for product_id in cart:
            try:
                p = Product.objects.get(id=product_id)
                cart_items.append(p)
                cart_total += float(p.price)
            except Product.DoesNotExist:
                pass

        response_data = {
            'success': True,
            'cart_total': cart_total,
            'cart_count': len(cart),
            'quantity': quantity
        }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(response_data)
    else:
        return redirect('cart')


# Удаление товара из корзины
def remove_from_cart(request, id):
    product = get_object_or_404(Product, id=id)

    if request.user.is_authenticated:
        # Для авторизованных удаляем запись CartItem
        CartItem.objects.filter(user=request.user, product=product).delete()
    else:
        # Для неавторизованных обновляем сессию
        cart = request.session.get('cart', {})
        if str(id) in cart:
            del cart[str(id)]
            request.session['cart'] = cart

    return redirect('cart')


# Очистка корзины
def clear_cart(request):
    if request.user.is_authenticated:
        # Для авторизованных удаляем все записи CartItem
        CartItem.objects.filter(user=request.user).delete()
    else:
        # Для неавторизованных очищаем сессию
        request.session['cart'] = {}

    return redirect('cart')


# API для получения счетчиков корзины и избранного
def get_counters(request):
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
        favorites_count = Favorite.objects.filter(user=request.user).count()

        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'favorites_count': favorites_count
        })

    return JsonResponse({
        'success': False,
        'error': 'User not authenticated'
    })


def update_recommendations(user=None):
    """
    Обновляет рекомендательные пары на основе содержимого корзин пользователей.
    Может быть вызвана для определенного пользователя или для всех пользователей.

    Эта функция анализирует товары, которые пользователи добавляют в корзину вместе,
    и создает/обновляет связи между ними для дальнейших рекомендаций.
    """
    with transaction.atomic():
        # Если указан конкретный пользователь, работаем только с его корзиной
        if user:
            cart_items = CartItem.objects.filter(user=user)
            if len(cart_items) > 1:
                # Создаем пары товаров из корзины
                products = [item.product for item in cart_items]
                for prod1, prod2 in combinations(products, 2):
                    if prod1.id != prod2.id:
                        # Убедимся, что prod1.id < prod2.id для избежания дублей
                        if prod1.id > prod2.id:
                            prod1, prod2 = prod2, prod1

                        # Ищем существующую запись или создаем новую
                        rec_pair, created = RecommendationPair.objects.get_or_create(
                            product1=prod1,
                            product2=prod2,
                            defaults={'score': 1.0}
                        )

                        if not created:
                            # Если запись уже существует, увеличиваем счет
                            rec_pair.score += 1.0
                            rec_pair.save()
        else:
            # Анализируем все корзины с более чем 1 товаром
            users_with_multiple_items = CartItem.objects.values('user').annotate(
                item_count=Count('id')
            ).filter(item_count__gt=1)

            for user_data in users_with_multiple_items:
                user_id = user_data['user']
                cart_items = CartItem.objects.filter(user_id=user_id)
                products = [item.product for item in cart_items]

                for prod1, prod2 in combinations(products, 2):
                    if prod1.id != prod2.id:
                        # Убедимся, что prod1.id < prod2.id для избежания дублей
                        if prod1.id > prod2.id:
                            prod1, prod2 = prod2, prod1

                        # Ищем существующую запись или создаем новую
                        rec_pair, created = RecommendationPair.objects.get_or_create(
                            product1=prod1,
                            product2=prod2,
                            defaults={'score': 1.0}
                        )

                        if not created:
                            # Если запись уже существует, увеличиваем счет
                            rec_pair.score += 1.0
                            rec_pair.save()

            # Нормализация значений score для более объективного ранжирования
            max_score = RecommendationPair.objects.aggregate(max_score=Max('score'))['max_score']
            if max_score and max_score > 0:
                # Используем SQL-запрос для обновления всех записей сразу
                RecommendationPair.objects.update(score=F('score') / max_score * 10.0)


def get_recommendations(product, user=None, session_id=None, limit=4):
    """
    Получить рекомендации для товара на основе нескольких факторов:
    1. Похожие товары из той же категории
    2. Товары, которые часто покупают вместе
    3. Персонализированные рекомендации на основе просмотров
    """
    # Проверяем кэш для этого товара и пользователя
    cache_key = f'recommendations_{product.id}_{user.id if user else "anon"}_{session_id or ""}'
    cached_recs = cache.get(cache_key)
    if cached_recs:
        return cached_recs

    # Результирующий список рекомендаций
    recommendations = []

    # 1. Рекомендации из той же категории - оптимизированный запрос с ограничением выборки
    category_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand')[:6]

    # 2. Товары, часто покупаемые вместе (из таблицы RecommendationPair)
    # Оптимизируем запрос, используя select_related для уменьшения количества обращений к БД
    related_by_pairs = RecommendationPair.objects.filter(
        Q(product1=product) | Q(product2=product)
    ).select_related('product1', 'product2').order_by('-score')[:8]

    related_products = []
    for pair in related_by_pairs:
        related_product = pair.product1 if pair.product2.id == product.id else pair.product2
        if related_product.is_active and related_product not in related_products:
            related_products.append(related_product)

    # 3. Персонализированные рекомендации на основе просмотров пользователя
    personalized = []

    if user and user.is_authenticated:
        # Находим последние просмотренные пользователем товары с оптимизацией запроса
        recent_views = ProductView.objects.filter(
            user=user
        ).exclude(
            product=product
        ).select_related('product').order_by('-timestamp')[:10]

        # На основе последних просмотров находим похожие товары по категориям и брендам
        viewed_products = [view.product for view in recent_views]
        viewed_categories = set(p.category_id for p in viewed_products if p.category_id)
        viewed_brands = set(p.brand_id for p in viewed_products if p.brand_id)

        if viewed_categories or viewed_brands:
            personalized_query = Product.objects.filter(is_active=True).exclude(id=product.id)

            if viewed_categories:
                personalized_query = personalized_query.filter(category_id__in=viewed_categories)

            if viewed_brands:
                personalized_query = personalized_query.filter(brand_id__in=viewed_brands)

            personalized = list(personalized_query.select_related('category', 'brand').distinct()[:6])

    elif session_id:
        # Рекомендации для анонимных пользователей на основе сессии
        recent_views = ProductView.objects.filter(
            session_id=session_id
        ).exclude(
            product=product
        ).select_related('product').order_by('-timestamp')[:5]

        viewed_products = [view.product for view in recent_views]
        viewed_categories = set(p.category_id for p in viewed_products if p.category_id)

        if viewed_categories:
            personalized = list(Product.objects.filter(
                category_id__in=viewed_categories,
                is_active=True
            ).exclude(id=product.id).select_related('category', 'brand').distinct()[:6])

    # Объединяем все рекомендации, избегая дубликатов
    all_recs = []

    # Сначала добавляем персонализированные рекомендации
    all_recs.extend(personalized)

    # Затем рекомендации на основе совместных покупок
    for product in related_products:
        if product not in all_recs and product.is_active:
            all_recs.append(product)

    # Затем товары из той же категории
    for product in category_products:
        if product not in all_recs and product.is_active:
            all_recs.append(product)

    # Если рекомендаций недостаточно, добавляем случайные товары
    if len(all_recs) < limit:
        random_products = Product.objects.filter(
            is_active=True
        ).exclude(
            id=product.id
        ).exclude(
            id__in=[p.id for p in all_recs]
        ).select_related('category', 'brand').order_by('?')[:limit - len(all_recs)]

        all_recs.extend(random_products)

    # Ограничиваем количество рекомендаций
    result = all_recs[:limit]

    # Кэшируем результат на 30 минут
    cache.set(cache_key, result, 30 * 60)

    return result


# API для переключения статуса товара (активен/неактивен)
@login_required
def toggle_product_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Только POST-запросы разрешены'})

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        is_active = data.get('is_active', False)

        if not product_id:
            return JsonResponse({'success': False, 'error': 'Не указан ID товара'})

        # Проверяем, что продукт принадлежит текущему пользователю
        try:
            product = Product.objects.get(id=product_id, seller=request.user)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден или у вас нет прав на его редактирование'})

        # Изменяем статус товара
        product.is_active = is_active
        product.save(update_fields=['is_active'])

        return JsonResponse({
            'success': True,
            'is_active': product.is_active,
            'message': 'Статус товара успешно изменен'
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Некорректный формат JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# API для удаления товара
@login_required
def delete_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Только POST-запросы разрешены'})

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse({'success': False, 'error': 'Не указан ID товара'})

        # Проверяем, что продукт принадлежит текущему пользователю
        try:
            product = Product.objects.get(id=product_id, seller=request.user)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден или у вас нет прав на его удаление'})

        # Удаляем товар и связанные с ним изображения
        product.delete()

        return JsonResponse({
            'success': True,
            'message': 'Товар успешно удален'
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Некорректный формат JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

#
# def product_list(request):
#     products = Product.objects.all()
#     favorites = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
#
#     return render(request, 'product_list.html', {
#         'products': products,
#         'favorites': favorites,
#     })


@login_required
def edit_product(request, id):
    """
    Редактирование существующего товара
    """
    product = get_object_or_404(Product, id=id, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            try:
                # Сохраняем обновленный продукт
                product = form.save()

                # Обработка загруженных фотографий (метод 1 - все сразу)
                if 'product_images' in request.FILES:
                    files = request.FILES.getlist('product_images')

                    # Проверяем количество загруженных файлов
                    if len(files) > 5:
                        files = files[:5]  # Ограничиваем максимум 5 файлов

                    # Удаляем существующие фотографии, если нужно заменить все
                    if request.POST.get('replace_all_images') == 'true':
                        ProductImage.objects.filter(product=product).delete()

                    # Определяем следующий порядковый номер
                    max_order = ProductImage.objects.filter(product=product).aggregate(Max('order'))[
                                    'order__max'] or -1

                    # Сохраняем фотографии
                    for i, file in enumerate(files):
                        is_main = False
                        if i == 0 and not ProductImage.objects.filter(product=product, is_main=True).exists():
                            is_main = True

                        ProductImage.objects.create(
                            product=product,
                            image=file,
                            is_main=is_main,
                            order=max_order + i + 1
                        )

                # Обработка удаления фотографий
                for key in request.POST:
                    if key.startswith('delete_image_') and request.POST[key] == 'true':
                        image_id = key.replace('delete_image_', '')
                        try:
                            image = ProductImage.objects.get(id=image_id, product=product)
                            # Проверяем, является ли удаляемое изображение главным
                            was_main = image.is_main
                            image.delete()
                            
                            # Если было удалено главное изображение, назначаем новое
                            if was_main:
                                # Выбираем первое доступное изображение и делаем его главным
                                first_image = ProductImage.objects.filter(product=product).order_by('order').first()
                                if first_image:
                                    first_image.is_main = True
                                    first_image.save()
                        except Exception as e:
                            print(f"Ошибка при удалении изображения: {e}")

                # Обработка изменения порядка фотографий
                # Сначала соберем все обновления порядка
                order_updates = {}
                for key in request.POST:
                    if key.startswith('image_order_'):
                        image_id = key.replace('image_order_', '')
                        try:
                            order_updates[int(image_id)] = int(request.POST[key])
                        except ValueError:
                            continue
                
                # Затем применим обновления порядка ко всем изображениям за один проход
                if order_updates:
                    # Получаем все изображения продукта
                    product_images = ProductImage.objects.filter(product=product)
                    
                    # Применяем обновления порядка
                    for image in product_images:
                        if image.id in order_updates:
                            image.order = order_updates[image.id]
                            image.save()
                
                # Обеспечиваем последовательность порядковых номеров
                images = ProductImage.objects.filter(product=product).order_by('order')
                for i, image in enumerate(images):
                    if image.order != i:
                        image.order = i
                        image.save()

                # Обработка смены главного фото
                if 'main_image' in request.POST and request.POST['main_image']:
                    try:
                        # Сначала сбрасываем главное фото у всех изображений
                        ProductImage.objects.filter(product=product).update(is_main=False)
                        
                        # Затем устанавливаем новое главное фото
                        image_id = request.POST['main_image']
                        image = ProductImage.objects.get(id=image_id, product=product)
                        image.is_main = True
                        image.save()
                    except Exception as e:
                        print(f"Ошибка при установке главного изображения: {e}")

                messages.success(request, "Товар успешно обновлен!")
                return redirect('product_detail', id=id)
            except Exception as e:
                print(f"Ошибка при обновлении товара: {e}")
                messages.error(request, f"Ошибка при обновлении товара: {e}")
        else:
            print(f"Форма невалидна: {form.errors}")
            messages.error(request, "Пожалуйста, проверьте введенные данные")
    else:
        form = ProductForm(instance=product)

    # Получаем существующие изображения товара
    product_images = ProductImage.objects.filter(product=product).order_by('order')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    main_image = product_images.filter(is_main=True).first()

    context = {
        'form': form,
        'product': product,
        'product_images': product_images,
        'main_image': main_image,
        'categories': categories,
        'brands': brands,
    }

    return render(request, 'html/accounts/edit_product.html', context)


@login_required
def add_product(request):
    # Проверяем, что пользователь - продавец
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'seller':
        return redirect('home')

    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # Создаем продукт без сохранения
                product = form.save(commit=False)
                product.seller = request.user  # Привязываем товар к текущему пользователю
                product.save()  # Сохраняем товар

                # Обработка загруженных фотографий (метод 1 - все сразу)
                if 'product_images' in request.FILES:
                    files = request.FILES.getlist('product_images')

                    # Проверяем количество загруженных файлов
                    if len(files) > 5:
                        files = files[:5]  # Ограничиваем максимум 5 файлов

                    # Сохраняем фотографии
                    for i, file in enumerate(files):
                        is_main = (i == 0)  # Первая фотография считается главной
                        ProductImage.objects.create(
                            product=product,
                            image=file,
                            is_main=is_main,
                            order=i
                        )

                # Обработка отдельных загруженных фотографий (метод 2 - по одной)
                for i in range(1, 6):  # Максимум 5 фотографий
                    field_name = f'product_image_{i}'
                    if field_name in request.FILES:
                        file = request.FILES[field_name]
                        max_order = ProductImage.objects.filter(product=product).aggregate(Max('order'))[
                                        'order__max'] or -1

                        # Создаем новое изображение
                        is_main = False
                        if i == 1 or not ProductImage.objects.filter(product=product, is_main=True).exists():
                            is_main = True

                        ProductImage.objects.create(
                            product=product,
                            image=file,
                            is_main=is_main,
                            order=max_order + 1
                        )

                # Перенаправляем на страницу профиля продавца
                return redirect('profile')
            except Exception as e:
                print(f"Ошибка при сохранении товара: {e}")
                return render(request, 'html/accounts/add_product.html', {
                    'form': form,
                    'error': f'Ошибка при сохранении товара: {e}',
                    'categories': categories,
                    'brands': brands
                })
        else:
            # Если форма не валидна, показываем ошибки
            return render(request, 'html/accounts/add_product.html', {
                'form': form,
                'categories': categories,
                'brands': brands
            })
    else:
        # GET запрос - показываем пустую форму
        form = ProductForm()
        return render(request, 'html/accounts/add_product.html', {
            'form': form,
            'categories': categories,
            'brands': brands
        })


def product_detail(request, id):
    # Пытаемся получить товар из кэша
    cache_key = f'product_detail_{id}'
    cached_product = cache.get(cache_key)

    if not cached_product:
        # Если нет в кэше, загружаем из БД с предварительной загрузкой связанных данных
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand', 'seller').prefetch_related('images'),
            id=id
        )
        # Сохраняем в кэш на 1 час
        cache.set(cache_key, product, 60 * 60)
    else:
        product = cached_product

    # Записываем просмотр товара
    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    # Создаем запись о просмотре
    try:
        if request.user.is_authenticated:
            ProductView.objects.create(
                user=request.user,
                product=product,
                session_id=session_id
            )
        else:
            ProductView.objects.create(
                product=product,
                session_id=session_id
            )
    except Exception as e:
        # В случае ошибки при записи просмотра, просто продолжаем работу
        print(f"Ошибка при сохранении просмотра: {e}")

    # Получаем информацию, избранное ли это для пользователя
    user_favorites = []
    if request.user.is_authenticated:
        # Оптимизируем запрос к избранному
        fav_products_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        user_favorites = list(fav_products_ids)

    # Также получим элементы корзины с оптимизацией
    user_cart_items = []
    if request.user.is_authenticated:
        user_cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    # Получаем рекомендации для данного товара
    recommended_products = get_recommendations(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        session_id=session_id
    )

    # Похожие товары из той же категории с оптимизацией запроса
    similar_products_cache_key = f'similar_products_{product.id}'
    similar_products = cache.get(similar_products_cache_key)

    if not similar_products:
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).select_related('category', 'brand').order_by('-created_at')[:4]

        # Кэшируем результат на 2 часа
        cache.set(similar_products_cache_key, similar_products, 2 * 60 * 60)

    context = {
        'product': product,
        'user_favorites': user_favorites,
        'user_cart': user_cart_items,
        'recommended_products': recommended_products,
        'similar_products': similar_products
    }

    return render(request, 'html/product_detail.html', context)
