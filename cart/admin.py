from django.contrib import admin
from cart.models import *


class FotogaleryShowRoomInline(admin.StackedInline):
    model = FotogaleryShowRoom


@admin.register(PageCartSeo)
class PageCartSeoAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'description',)


@admin.register(DeliveryPageSeo)
class DeliveryPageSeoAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'description',)
    inlines = [FotogaleryShowRoomInline]


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(StandartSale)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(DeliveryType)
