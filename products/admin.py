from django.contrib import admin
from django.contrib.auth.models import User

from .models import Product, Favorite, CartItem, Brand, Category, ProductImage, ProductView, RecommendationPair

# Register your models here.
admin.site.register(Product)
admin.site.register(Favorite)
admin.site.register(CartItem)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ProductImage)



@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'session_id', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__email', 'product__name', 'session_id']
    date_hierarchy = 'timestamp'

@admin.register(RecommendationPair)
class RecommendationPairAdmin(admin.ModelAdmin):
    list_display = ['product1', 'product2', 'score', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['product1__name', 'product2__name']
    ordering = ['-score']

# admin.py

from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Product, ProductImage

# Ограничивающий formset
class ProductImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = sum(
            1 for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        )
        if count > 5:
            raise ValidationError("Можно загрузить не более 5 фотографий.")

# Inline для изображений
class ProductImageInline(admin.TabularInline):  # Или StackedInline, если так больше нравится
    model = ProductImage
    formset = ProductImageInlineFormSet
    extra = 1  # Сколько пустых форм показывать по умолчанию

# Админка для Product с инлайном изображений

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'seller', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
