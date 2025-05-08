
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_main', 'image_optional', 'is_active']


    # Переопределяем clean метод для более сложной валидации
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Цена товара должна быть больше нуля.")
        return cleaned_data
