from django.db import models


class Articles(models.Model):
    title = models.CharField('Название', max_length=100, default='Обновление')
    announce = models.CharField('Анонс', max_length=250)
    text = models.TextField('Основной текст')
    date = models.DateTimeField('Дата публикации')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'