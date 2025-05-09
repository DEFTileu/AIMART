from django import forms
from .models import Product, ProductImage



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'brand', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Цена товара должна быть больше нуля.")
        return cleaned_data

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main']

