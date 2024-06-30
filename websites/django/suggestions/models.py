from django.db import models


class Suggestions(models.Model):
    title = models.CharField('Название', max_length=100)
    text = models.TextField('Основной текст')
    date = models.DateTimeField('Дата публикации')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'