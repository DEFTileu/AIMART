from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Card

class LoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'id_email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_password'}))

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'id_email'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'id_full_name'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'id': 'id_password1'}))
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'id': 'id_password2'}))

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Проверяем длину пароля
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')

        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Проверяем, что пароли совпадают
        if password1 != password2:
            raise forms.ValidationError('The two password fields must match.')

        return password2

# class CardForm(forms.ModelForm):
#     class Meta:
#         model = Card
#         fields = ['card_number', 'expiry_date', 'card_holder', 'cvv']
#         widgets = {
#             'card_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'XXXX XXXX XXXX XXXX',
#                 'pattern': r'\d{4}\s\d{4}\s\d{4}\s\d{4}'
#             }),
#             'expiry_date': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'MM/YY',
#                 'pattern': r'(0[1-9]|1[0-2])/([0-9]{2})'
#             }),
#             'card_holder': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'ИМЯ НА КАРТЕ'
#             }),
#             'cvv': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'CVV',
#                 'pattern': r'\d{3,4}'
#             })
#         }
#
#     def clean_card_number(self):
#         card_number = self.cleaned_data['card_number']
#         # Удаляем все пробелы для проверки
#         card_number_clean = card_number.replace(' ', '')
#         if not card_number_clean.isdigit() or len(card_number_clean) != 16:
#             raise forms.ValidationError('Неверный номер карты')
#         # Возвращаем номер с пробелами
#         return ' '.join([card_number_clean[i:i+4] for i in range(0, 16, 4)])
