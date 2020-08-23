from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Нельзя добавлять еще элементы, можно исправлять элемент: %s" % model.__name__)


class ShowRoomModel(models.Model):
    name_element = models.CharField(max_length=100,
                                    help_text='название элемента, до 100 символов',
                                    default='Страница ShowRoom',
                                    verbose_name='Название элемента')
    title_showroom_page = models.CharField(max_length=200,
                                           help_text='до 200 символов',
                                           default='Title страницы',
                                           verbose_name='Title страницы')
    description_showroom_page = models.CharField(max_length=450,
                                                 help_text='до 450 символов',
                                                 default='Description страницы',
                                                 verbose_name='Description страницы')
    name = models.CharField(max_length=200,
                            help_text='длина до 200 символов',
                            verbose_name='Заголовок на странице')
    slug = models.SlugField(max_length=200,
                            verbose_name='(Ссылка)',
                            help_text='URL-адрес до 200 символов',
                            blank=True)
    content = models.TextField(help_text='длина до 3000 символов',
                               verbose_name='Содержимое')

    class Meta:
        verbose_name = 'Страница ShowRoom: настройки'
        verbose_name_plural = 'Страница ShowRoom: настройки'

    def __str__(self):
        return self.name_element

    def clean(self):
        validate_only_one_instance(self)

    def get_absolute_url(self):
        return reverse('showroom:showroom_view', args=[self.slug])


class Fotogalery(models.Model):
    """
    Модель фото для страницы ShowRoom
    """
    showroomimg = models.ForeignKey(ShowRoomModel,
                                related_name='fotos',
                                on_delete=models.CASCADE)
    altimg = models.CharField(max_length=150,
                              blank=True,
                              help_text='Атрибут ALT для изображения, необязательно',
                              verbose_name='ALT')
    docfile = models.FileField(upload_to='showroom_images/',
                               blank=True,
                               null=True,
                               verbose_name='Загрузить фото')

    class Meta:
        verbose_name = 'Фотогалерея'
        verbose_name_plural = 'Изображения на странице'


class Content(models.Model):
    """
    Модель обобщенного типа для фото
    """
    module = models.ForeignKey(Fotogalery, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
