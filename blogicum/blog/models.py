from django.contrib.auth import get_user_model
from django.db import models

from core.models import PublishedModel

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(max_length=256,
                             verbose_name="Заголовок")
    description = models.TextField(
        verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text='Идентификатор страницы для URL;'
                  ' разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
        verbose_name="Название места")

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок")
    text = models.TextField(
        verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату'
                  ' и время в будущем — можно'
                  ' делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post',
        verbose_name='Автор публикации')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 related_name='post',
                                 null=True, blank=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 related_name='post',
                                 null=True,
                                 verbose_name='Категория')
    image = models.ImageField('Фото', blank=True, upload_to='posts_images')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
