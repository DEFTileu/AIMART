from django.db import models

# Create your models here.
class News(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    image = models.ImageField("Изображение", upload_to='news/', null=True, blank=True)
    short_description = models.TextField("Краткое описание", max_length=300)
    content = models.TextField("Содержание")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    views_count = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/news/{self.slug}/'

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])