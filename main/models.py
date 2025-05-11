from django.db import models
from django.conf import settings

class Banner(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to='banners/')
    button_text = models.CharField("Текст кнопки", max_length=50, default="Подробнее", blank=True)
    button_url = models.CharField("Ссылка", max_length=255)
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

