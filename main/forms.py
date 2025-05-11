from django import forms
from .models import Banner

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'description', 'image', 'button_text', 'button_url', 'is_active', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'button_url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['button_text'].required = False

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("Размер изображения не должен превышать 2MB")
        return image
