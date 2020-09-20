from django.db import models
from product.models import Sizes
from authuser.models import ShopUser
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Нельзя добавлять еще элементы, можно исправлять элемент: %s" % model.__name__)


class PageCartSeo(models.Model):
    """
    Страница корзина: SEO настройки
    (чаще скрывают от индексации)
    """
    name = models.CharField(max_length=100,
                            default='Страница - Корзина',
                            help_text='Модель для хранения SEO на странице Корзина',
                            verbose_name='Название страницы')
    title = models.CharField(max_length=200,
                             blank=True,
                             default='Корзина',
                             help_text='Длина Title до 200 символов',
                             verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   default='Корзина',
                                   help_text='Длина Description до 450 символов',
                                   verbose_name='SEO Description')

    class Meta:
        verbose_name = '02: SEO для Корзины'
        verbose_name_plural = '02: SEO для Корзины'

    def __str__(self):
        return self.name

    def clean(self):
        validate_only_one_instance(self)


class CartItem(models.Model):
    product = models.ForeignKey(Sizes, on_delete=models.CASCADE, null=True)
    count = models.PositiveSmallIntegerField(default=1)
    color = models.CharField(max_length=100, blank=True, null=True)
    price_per_item_color = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_price = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Товары в корзине'

    def __str__(self):
        return self.product.product.name


class Cart(models.Model):
    products = models.ManyToManyField(CartItem, blank=True, verbose_name='Продукты')
    total_price = models.PositiveIntegerField(default=0, verbose_name='Итоговая сумма')

    class Meta:
        verbose_name = '03: Корзина: товары в корзине'
        verbose_name_plural = '03: Корзины: товары в корзине'

    def __str__(self):
        return '%s%d' % ('Cart', self.id)

    def add_to_cart(self, product, color=None, default_count=1):
        cart = self
        new_item, _ = CartItem.objects.get_or_create(product=product, count=default_count,
                                                     total_price=product.saleprice * default_count)
        if new_item not in cart.products.all():
            if not color is None:
                new_item.color = color.color.name
                new_item.total_price = color.price * default_count
                new_item.price_per_item_color = color.price
                new_item.save()
            cart.products.add(new_item)
            cart.total_price += new_item.total_price
            cart.save()

    def remove_from_cart(self, product):
        cart = self
        for cart_item in cart.products.all():
            if cart_item.product == product:
                cart.products.remove(cart_item)
                cart_item.delete()
                cart.total_price -= cart_item.total_price
                cart.save()


class StandartSale(models.Model):
    sale = models.PositiveSmallIntegerField(default=0, verbose_name='Стандартная скидка')

    def __str__(self):
        return "{0} %".format(self.sale)

    class Meta:
        verbose_name = '04: Стандартная скидка'
        verbose_name_plural = '04: Стандартная скидка'


class OrderItems(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Sizes, on_delete=models.CASCADE, null=True)
    count = models.PositiveSmallIntegerField(default=1)
    color = models.CharField(max_length=100, blank=True, null=True)
    total_price = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Продукт в заказе'
        verbose_name_plural = 'Продукт в заказе'


class DeliveryType(models.Model):
    image = models.ImageField(upload_to='delivery_images', verbose_name='Изображение')
    description = models.CharField(max_length=1000, verbose_name='Описание')

    class Meta:
        verbose_name = 'Информация о доставке'
        verbose_name_plural = 'Информация о доставке'

    def __str__(self):
        return "Доставка {0}".format(self.id)


class Order(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Имя')
    full_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='ФИО')
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name='Телефон')
    email = models.CharField(max_length=150, blank=True, null=True, verbose_name='Почта')
    delivery_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Способ доставки')
    delivery_region = models.CharField(max_length=100, blank=True, null=True, verbose_name='Регион')
    delivery_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    delivery_street = models.CharField(max_length=100, blank=True, null=True, verbose_name='Улица')
    delivery_house = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Номер дома')
    delivery_padik = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Номер подъезда')
    delivery_flat = models.PositiveIntegerField(blank=True, null=True, verbose_name='Квартира')
    delivery_deadline = models.CharField(max_length=100, blank=True, null=True, verbose_name='Сроки')
    take_away_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Адрес при самовывозе')
    transport_company_address = models.CharField(max_length=100, blank=True, null=True,
                                                 verbose_name='Адрес транспортной компании')
    payment_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Тип оплаты')
    org_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Наименование организации')
    inn = models.CharField(max_length=20, blank=True, null=True, verbose_name='ИНН')
    legal_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Юридический адрес')
    additional_information = models.TextField(blank=True, null=True, verbose_name='Дополнительная информация')
    STATUS_TYPES = (
        ('Оформлен', 'Оформлен'),
        ('Выполнен', 'Выполнен'),
        ('Доставлен', 'Доставлен'),
        ('Отменен', 'Отменен'),
        ('Выдан', 'Выдан')
    )
    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='Оформлен')
    total_price = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '05: Заказ'
        verbose_name_plural = '05: Заказы'

    def __str__(self):
        return "Заказ №{0}".format(self.id)


class DeliveryPageSeo(models.Model):
    """
    Страница Доставка: настройки
    """
    name = models.CharField(max_length=100,
                            default='Доставка',
                            help_text='Модель для хранения SEO на странице Доставка',
                            verbose_name='Название страницы')
    title = models.CharField(max_length=200,
                             blank=True,
                             default='Доставка в интернет-магазине Маргроид',
                             help_text='Длина Title до 200 символов',
                             verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   default='Доставка в интернет-магазине Маргроид',
                                   help_text='Длина Description до 450 символов',
                                   verbose_name='SEO Description')
    content = models.TextField(max_length=3000,
                               blank=True,
                               help_text='длина до 3000 символов',
                               verbose_name='Содержимое')

    class Meta:
        verbose_name = '01: Настройки - Доставка'
        verbose_name_plural = '01: Настройки страницы Доставка'

    def __str__(self):
        return self.name

    def clean(self):
        validate_only_one_instance(self)


class FotogaleryShowRoom(models.Model):
    """
    Модель фото для страницы Доставка (имя модели забыл переименовать)
    """
    showroomimg = models.ForeignKey(DeliveryPageSeo,
                                    related_name='fotosdelivery',
                                    on_delete=models.CASCADE)
    desc_img = models.CharField(max_length=150,
                              blank=True,
                              help_text='Описание преимущества до 150 символов',
                              verbose_name='Описание преимущества до 150 символов')
    altimg = models.CharField(max_length=150,
                              blank=True,
                              help_text='Атрибут ALT для изображения, необязательно',
                              verbose_name='ALT')
    docfile = models.FileField(upload_to='delivery_images/',
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
    module = models.ForeignKey(FotogaleryShowRoom, related_name='fotocontentdelivery', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, related_name='contentstypedelivery', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
