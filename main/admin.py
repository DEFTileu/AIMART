# main/admin.py
from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')