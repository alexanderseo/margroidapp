from django.db import models
from django.conf import settings


class ShopUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    discount = models.PositiveSmallIntegerField(default=0, blank=True, verbose_name='Скидка')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Пользователи'
