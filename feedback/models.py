from django.db import models


class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    message = models.CharField(max_length=255, verbose_name='Сообщение')

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name}'
