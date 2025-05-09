from django import forms
from .models import News
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import re


class NewsForm(forms.ModelForm):
    """Форма для создания и редактирования новостей"""

    class Meta:
        model = News
        fields = ['title', 'image', 'short_description', 'content', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок новости'}),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Краткое описание (максимум 300 символов)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Полное содержание новости'
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_title(self):
        """Проверка и очистка заголовка"""
        title = self.cleaned_data.get('title', '')
        if len(title) < 5:
            raise ValidationError("Заголовок должен содержать не менее 5 символов")
        return title

    def clean_short_description(self):
        """Проверка и очистка краткого описания"""
        short_description = self.cleaned_data.get('short_description', '')
        if len(short_description) < 10:
            raise ValidationError("Краткое описание должно содержать не менее 10 символов")
        return short_description

    def save(self, commit=True):
        """Переопределяем метод сохранения для автоматического создания slug"""
        instance = super().save(commit=False)

        # Создаем slug из заголовка
        base_slug = slugify(instance.title)

        # Транслитерация кириллицы, если требуется
        base_slug = self.transliterate(base_slug)

        # Проверяем уникальность slug
        slug = base_slug
        counter = 1
        while News.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        instance.slug = slug

        if commit:
            instance.save()
        return instance

    def transliterate(self, text):
        """Простая транслитерация кириллических символов"""
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
            'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya', ' ': '-', '_': '-'
        }

        result = ''
        for char in text.lower():
            result += translit_dict.get(char, char)

        # Удаляем все символы, кроме латинских букв, цифр и дефиса
        result = re.sub(r'[^a-z0-9\-]', '', result)

        # Убираем повторяющиеся дефисы
        result = re.sub(r'\-+', '-', result)

        return result
