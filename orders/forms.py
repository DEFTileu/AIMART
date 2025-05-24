from django import forms
from .models import Order, SavedCard

class PaymentForm(forms.Form):
    PAYMENT_METHODS = (
        ('CARD', 'Банковская карта'),
        ('KASPI', 'Kaspi'),
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect,
        label='Способ оплаты'
    )
    
    save_card = forms.BooleanField(
        required=False,
        label='Сохранить карту для будущих платежей'
    )

class CardPaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=19,
        min_length=16,
        label='Номер карты',
        widget=forms.TextInput(attrs={
            'placeholder': '0000 0000 0000 0000',
            'pattern': '[0-9\s]{16,19}',
            'inputmode': 'numeric'
        })
    )
    
    expiry_month = forms.ChoiceField(
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
        label='Месяц'
    )
    
    expiry_year = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(2024, 2035)],
        label='Год'
    )
    
    cvv = forms.CharField(
        max_length=4,
        min_length=3,
        label='CVV',
        widget=forms.TextInput(attrs={
            'placeholder': '123',
            'pattern': '[0-9]{3,4}',
            'inputmode': 'numeric'
        })
    )
    
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not card_number.isdigit():
            raise forms.ValidationError('Номер карты должен содержать только цифры')
        return card_number
    
    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit():
            raise forms.ValidationError('CVV должен содержать только цифры')
        return cvv 