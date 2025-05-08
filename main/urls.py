from django.contrib import admin
from django.urls import path,include

from main.views import home, base, about, catalog, favorites, login, add_product, cart, product_detail, add_to_cart, \
        add_to_wishlist, seller_profile, toggle_favorite
from accounts.views import auth_view

urlpatterns = [
        path('',home,name='home',),
        path('base/',base,name='base'),
        path('about/',about,name='about'),
        path('catalog/',catalog,name='catalog'),
        path('favorites/',favorites,name='favorites'),
        path('cart/',cart,name='cart'),
        path('login/',login,name='login'),
        path('auth/', auth_view, name='auth'),
        path('add-product/', add_product, name='add_product'),
        path('product/<int:id>/', product_detail, name='product_detail'),
        path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
        path('add_to_wishlist/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
        path('seller_profile/<int:seller_id>/', seller_profile, name='seller_profile'),
        path('api/favorites/toggle/', toggle_favorite, name='toggle_favorite'),




]
