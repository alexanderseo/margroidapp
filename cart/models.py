from django.db import models
from product.models import Sizes
from auth.models import ShopUser


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
    products = models.ManyToManyField(CartItem, blank=True)
    total_price = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Корзины'

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
        verbose_name_plural = 'Стандартная скидка'


class OrderItems(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Sizes, on_delete=models.CASCADE, null=True)
    count = models.PositiveSmallIntegerField(default=1)
    color = models.CharField(max_length=100, blank=True, null=True)
    total_price = models.PositiveIntegerField(default=0)


class DeliveryType(models.Model):
    image = models.ImageField(upload_to='delivery_images', verbose_name='Изображение')
    description = models.CharField(max_length=1000, verbose_name='Описание')

    class Meta:
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
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return "Заказ №{0}".format(self.id)
