from django.contrib import admin
from django.urls import path,include

from main.views import home, base, about, cart, seller_profile, faq
from products.views import product_detail, catalog, favorites, cart_view, add_product, edit_product, delete_product, \
        add_to_cart, add_to_wishlist, toggle_favorite, cart_ajax, get_counters, toggle_product_status, update_cart, \
        remove_from_cart, clear_cart
from accounts.views import auth_view

urlpatterns = [
        path('',home,name='home',),
        path('base/',base,name='base'),
        path('about/',about,name='about'),
        path('catalog/',catalog,name='catalog'),
        path('favorites/',favorites,name='favorites'),
        path('cart/',cart_view,name='cart'),
        path('auth/', auth_view, name='auth'),
        path('add-product/', add_product, name='add_product'),
        path('product/<int:id>/', product_detail, name='product_detail'),
        path('edit-product/<int:id>/', edit_product, name='edit_product'),
        path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
        path('add_to_wishlist/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
        path('seller_profile/<int:seller_id>/', seller_profile, name='seller_profile'),
        path('api/favorites/toggle/', toggle_favorite, name='toggle_favorite'),
        path('api/cart/ajax/', cart_ajax, name='cart_ajax'),
        path('api/counters/', get_counters, name='get_counters'),
        path('api/products/toggle-status/', toggle_product_status, name='toggle_product_status'),
        path('api/products/delete/', delete_product, name='delete_product'),
        path('update_cart/<int:id>/', update_cart, name='update_cart'),
        path('remove_from_cart/<int:id>/', remove_from_cart, name='remove_from_cart'),
        path('clear_cart/', clear_cart, name='clear_cart'),
        path('faq/', faq, name='faq'),
]
