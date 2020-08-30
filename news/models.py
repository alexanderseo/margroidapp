from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Нельзя добавлять еще элементы, можно исправлять элемент: %s" % model.__name__)


class PageNewsSeo(models.Model):
    """
    Страница новостей: SEO настройки
    (общая страница)
    """
    name = models.CharField(max_length=100,
                            default='Страница - Новости',
                            help_text='Модель для хранения SEO на странице Новости',
                            verbose_name='Название страницы')
    title = models.CharField(max_length=200,
                             blank=True,
                             default='Новости на сайте интернет-магазина Маргроид',
                             help_text='Длина Title до 200 символов',
                             verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   default='Новости на сайте интернет-магазина Маргроид',
                                   help_text='Длина Description до 450 символов',
                                   verbose_name='SEO Description')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.name

    def clean(self):
        validate_only_one_instance(self)


class News(models.Model):
    """
    Одиночная статья
    """
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
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:detail_news_view', args=[self.slug])
