from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser

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
