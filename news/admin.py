from django.contrib import admin

from news.models import News


# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published', 'views_count')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'short_description', 'content')
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'image', 'short_description', 'content')
        }),
        ('Настройки публикации', {
            'fields': ('is_published',)
        }),
        ('Статистика', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )