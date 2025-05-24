from django.contrib import admin
from .models import Order, OrderItem, SavedCard

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'user', 'total', 'payment_method', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['number', 'user__email', 'user__username']
    readonly_fields = ['number', 'created_at', 'paid_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'user', 'total', 'payment_method', 'status')
        }),
        ('Даты', {
            'fields': ('created_at', 'paid_at')
        }),
    )

@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_type', 'last_four', 'expiry_month', 'expiry_year', 'created_at']
    list_filter = ['card_type', 'created_at']
    search_fields = ['user__email', 'user__username', 'last_four']
    readonly_fields = ['created_at']
