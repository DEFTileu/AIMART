from django.contrib import admin

from main.models import Product, Favorite, CartItem

# Register your models here.
admin.site.register(Product)
admin.site.register(Favorite)
admin.site.register(CartItem)