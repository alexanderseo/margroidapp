from django.db import models
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from authuser.models import ShopUser


class CategoryChild(models.Model):
    """
    Модель подкатегории товара
    """
    name = models.CharField(max_length=100,
                            help_text='длина до 100 символов',
                            verbose_name='Название подкатегории')
    title = models.CharField(max_length=200,
                             blank=True,
                             null=True,
                             help_text='длина до 200 символов',
                             verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   null=True,
                                   help_text='длина до 450 символов',
                                   verbose_name='SEO Description')
    image = models.ImageField(upload_to='category_images',
                              null=True,
                              verbose_name='Изображение')
    slug = models.SlugField(max_length=100,
                            help_text='длина до 100 символов',
                            verbose_name='URL-адрес')

    class Meta:
        verbose_name = '02: Подкатегория'
        verbose_name_plural = '02: Подкатегории'

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель категории товара
    """
    name = models.CharField(max_length=100,
                            help_text='длина до 100 символов',
                            verbose_name='Название категории')
    title = models.CharField(max_length=200,
                             blank=True,
                             null=True,
                             help_text='длина до 200 символов',
                             verbose_name='SEO Title')
    description = models.CharField(max_length=450,
                                   blank=True,
                                   null=True,
                                   help_text='длина до 450 символов',
                                   verbose_name='SEO Description')
    image = models.ImageField(upload_to='category_images',
                              null=True,
                              verbose_name='Изображение категории')
    slug = models.SlugField(max_length=100,
                            help_text='длина на латинице до 100 символов',
                            verbose_name='URL-адрес')
    subtype = models.ManyToManyField(CategoryChild,
                                     blank=True,
                                     verbose_name='Подкатегории')

    class Meta:
        verbose_name = '01: Категория'
        verbose_name_plural = '01: Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail_view', args=[self.slug])


class Product(models.Model):
    """
    Модель товара. Товар имеет:
    - базовую цену
    - скидку
    - размеры (у каждого размера своя цена)
    - цвета (у каждого цвета своя цена)
    """
    name = models.CharField(max_length=200, verbose_name='Имя')
    title = models.CharField(max_length=200,
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    sub_category = models.ForeignKey(CategoryChild, on_delete=models.CASCADE, null=True, verbose_name='Подкатегория',
                                     blank=True)
    image = models.ImageField(upload_to='product_images', null=True, verbose_name='Изображение')
    textproduct = models.TextField(blank=True,
                                   null=True,
                                   help_text='описание товара необязательно',
                                   verbose_name='Описание товара')
    vendor_code = models.CharField(max_length=100, verbose_name='Артикул', blank=True)
    in_stock = models.PositiveIntegerField(default=0, verbose_name='Наличие (шт)')
    complect = models.ManyToManyField('Product', verbose_name='Комплектующие', blank=True)
    color = models.ManyToManyField('Colors', verbose_name='Цвета', blank=True)
    price = models.PositiveIntegerField(null=True, verbose_name='Цена')
    on_sale = models.BooleanField(default=False, blank=True, verbose_name='На скидке')
    sale = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Размер скидки')
    new_price = models.PositiveIntegerField(blank=True, null=True, help_text='Вычисляется само при сохранении',
                                            verbose_name='Новая цена')
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def get_new_price(self):
        new_price = self.price
        if self.on_sale:
            percent = Decimal((100 - self.sale) / 100)
            new_price = self.price * percent.quantize(Decimal('1.00'))
        return new_price

    def save(self, *args, **kwargs):
        self.new_price = self.get_new_price
        super(Product, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-category', 'name', 'price']
        verbose_name = '03: Товар'
        verbose_name_plural = '03: Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail_view', args=[self.id])


class Fotogalery(models.Model):
    """
    Модель фото товаров
    """
    product = models.ForeignKey(Product,
                                related_name='fotos',
                                on_delete=models.CASCADE)
    altimg = models.CharField(max_length=150,
                              blank=True,
                              help_text='Атрибут ALT для изображения, необязательно',
                              verbose_name='ALT')
    docfile = models.FileField(upload_to='product_images/',
                               blank=True,
                               null=True,
                               verbose_name='Загрузить фото товара')

    class Meta:
        verbose_name = 'Фотогалерея'
        verbose_name_plural = 'Изображения товара'


class Content(models.Model):
    """
    Модель обобщенного типа для фото товаров
    """
    module = models.ForeignKey(Fotogalery, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')


class Sizes(models.Model):
    """
    Модель размеров товара
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Продукт')
    height = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Высота')
    width = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Ширина')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    saleprice = models.PositiveIntegerField(blank=True, null=True, help_text='Вычисляется само при сохранении',
                                            verbose_name='Цена размера по скидке')

    # Функциональное поле, для определения цены со скидкой по всем размерам
    @property
    def new_price_with_sale_on_all_size(self):
        saleprice = self.price
        sizeproduct = self.product
        if sizeproduct.on_sale:
            percent = Decimal((100 - sizeproduct.sale) / 100)
            saleprice = self.price * percent.quantize(Decimal('1.00'))
        return saleprice

    def save(self, *args, **kwargs):
        self.saleprice = self.new_price_with_sale_on_all_size
        super(Sizes, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.saleprice = self.new_price_with_sale_on_all_size
        super(Sizes, self).update(*args, **kwargs)

    class Meta:
        verbose_name = '04: Размер товара'
        verbose_name_plural = '04: Размеры'

    def __str__(self):
        return "{0} ({1}*{2}) - (ID размера: {3} - ID товара {4})".format(self.product.name, self.height, self.width, self.id, self.product_id)


# Сигнал, если товар сохранился со скидкой, то пересохраняем цены у размеров
@receiver(post_save, sender=Product)
def update_price_for_size(sender, instance, **kwargs):
    product = Product.objects.get(name=instance)
    savesize = Sizes.objects.filter(product=product)
    for ss in savesize:
        ss.save()


class Colors(models.Model):
    """
    Модель цвета
    """
    name = models.CharField(max_length=100, verbose_name='Название цвета')
    image = models.ImageField(upload_to='product_colors', null=True, verbose_name='Изображение')
    price = models.PositiveIntegerField(default=3000, verbose_name='Цена')

    class Meta:
        verbose_name = '05: Цвет товара'
        verbose_name_plural = '05: Цвета'

    def __str__(self):
        return self.name


class Comment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, null=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return "Комментарий к продукту {0} от {1}".format(self.product.name, self.user.user.username)


class ProductColorsSizes(models.Model):
    """
    Модель из старой логики сайта,
    чтобы не переписывать некотрые функции в карточке товара и корзине,
    сюда сохраняется связь цвета и размера
    """
    product = models.ForeignKey(Sizes, on_delete=models.CASCADE, verbose_name='Продукт (с размером)')
    color = models.ForeignKey(Colors, on_delete=models.CASCADE, verbose_name='Цвет')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    saleprice = models.PositiveIntegerField(blank=True,
                                            null=True,
                                            help_text='Вычисляется само при сохранении',
                                            verbose_name='Цена по скидке')

    # Общая цена для цвета
    @property
    def price_color_plus_product_price(self):
        from_product_price = self.product.product.price
        base_color_price = self.color.price
        total_price = from_product_price + base_color_price
        return total_price

    # Функциональное поле, для цены со скидкой по всем размерам и цветам
    @property
    def new_price_with_sale_with_size_on_color(self):
        sizecolorproduct = self.product.price
        skidka = self.product.product
        colorprice = self.color.price
        if skidka.on_sale:
            percent = Decimal((100 - skidka.sale) / 100)
            saleprice = colorprice + sizecolorproduct * percent.quantize(Decimal('1.00'))
            return saleprice
        else:
            return self.price

    def save(self, *args, **kwargs):
        self.price = self.price_color_plus_product_price
        self.saleprice = self.new_price_with_sale_with_size_on_color
        super(ProductColorsSizes, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Цены цветов'

    def __str__(self):
        return "{0} - {1}".format(self.product.product.name, self.color.name)


@receiver(post_save, sender=Colors)
def update_price_for_colorsize(sender, instance, **kwargs):
    """
    Сигнал, если базовая цена цвета изменилась, то изменилась ProductColorsSizes
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    color = Colors.objects.get(name=instance)
    savecolorsize = ProductColorsSizes.objects.filter(color=color)
    for ss in savecolorsize:
        ss.save()
