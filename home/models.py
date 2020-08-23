from django.db import models
from django.core.exceptions import ValidationError


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Нельзя добавлять еще элементы, можно исправлять элемент: %s" % model.__name__)


class Header(models.Model):
    name_element = models.CharField(max_length=100,
                                    help_text='название элемента, до 100 символов',
                                    default='Шапка сайта',
                                    verbose_name='Название элемента')
    header_logo = models.ImageField(blank=False,
                                    upload_to='logo/',
                                    help_text='изображение может обрезаться',
                                    verbose_name='Логотип сайта')
    alt_logo_header = models.CharField(max_length=100,
                                       blank=True,
                                       help_text='Атрибут ALT для SEO, до 100 символов',
                                       verbose_name='Атрибут ALT для логотипа')
    phone_one = models.CharField(max_length=20,
                                 blank=True,
                                 help_text='пишется ф формате: +7(999)-888-6655',
                                 verbose_name='Номер телефона 1')
    phone_two = models.CharField(max_length=20,
                                 blank=True,
                                 help_text='пишется ф формате: +7(999)-888-6655',
                                 verbose_name='Номер телефона 2')

    class Meta:
        verbose_name = 'Шапка сайта: настройки'
        verbose_name_plural = 'Шапка сайта: настройки'

    def __str__(self):
        return self.name_element

    def clean(self):
        validate_only_one_instance(self)


class SeoHomePage(models.Model):
    name_element = models.CharField(max_length=100,
                                    help_text='название элемента, до 100 символов',
                                    default='Мета-теги главной страницы',
                                    verbose_name='Название элемента')
    title_home_page = models.CharField(max_length=200,
                                       help_text='до 200 символов',
                                       default='Title главной страницы',
                                       verbose_name='Title главной страницы')
    description_home_page = models.CharField(max_length=450,
                                             help_text='до 450 символов',
                                             default='Description главной страницы',
                                             verbose_name='Description главной страницы')

    class Meta:
        verbose_name = 'Главная страница: SEO'
        verbose_name_plural = 'Главная страница: SEO'

    def __str__(self):
        return self.name_element

    def clean(self):
        validate_only_one_instance(self)


