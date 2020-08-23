from django.db import models
from django.urls import reverse


class News(models.Model):
    name = models.CharField(max_length=200,
                             help_text='длина до 200 символов',
                             verbose_name='Заголовок статьи')
    titleseo = models.CharField(max_length=200,
                                blank=True,
                                null=True,
                                help_text='длина до 200 символов',
                                verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   null=True,
                                   help_text='длина до 450 символов',
                                   verbose_name='SEO Description')
    slug = models.SlugField(max_length=200,
                            verbose_name='(Ссылка)',
                            help_text='URL-адрес до 200 символов',
                            blank=True)
    content = models.TextField(max_length=3000,
                               help_text='длина до 3000 символов',
                               verbose_name='Содержимое')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:detail_news_view', args=[self.slug])
