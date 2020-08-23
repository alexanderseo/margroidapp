from django.db import models


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