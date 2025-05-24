from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import re


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('customer', 'Заказчик'),
        ('seller', 'Продавец'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/avatar.png'
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Указываем кастомный менеджер
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Поле для аутентификации
    REQUIRED_FIELDS = ['full_name']  # Обязательные поля для суперпользователя

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Имеет ли пользователь конкретное разрешение."""
        return True

    def has_module_perms(self, app_label):
        """Имеет ли пользователь доступ к указанному приложению."""
        return True




class Card(models.Model):
    CARD_TYPES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'MasterCard'),
        ('AMEX', 'American Express'),
        ('MAESTRO', 'Maestro'),
        ('MIR', 'МИР'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_cards')

    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    card_number = models.CharField(max_length=19)  # формат: XXXX XXXX XXXX XXXX
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    card_holder = models.CharField(max_length=100)
    cvv = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Валидация номера карты (формат XXXX XXXX XXXX XXXX)
        if not re.match(r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$', self.card_number):
            raise ValidationError('Неверный формат номера карты. Ожидается XXXX XXXX XXXX XXXX')

        # Валидация expiry_month
        if not (1 <= self.expiry_month <= 12):
            raise ValidationError('Месяц истечения должен быть от 1 до 12')

        # Валидация expiry_year (например, от текущего года и выше)
        import datetime
        current_year = datetime.datetime.now().year
        if self.expiry_year < current_year:
            raise ValidationError('Год истечения карты не может быть в прошлом')

        # Валидация CVV (3-4 цифры)
        if not re.match(r'^\d{3,4}$', self.cvv):
            raise ValidationError('CVV должен содержать 3 или 4 цифры')

    def __str__(self):
        return f"{self.card_holder} - **** **** **** {self.card_number[-4:]}"

