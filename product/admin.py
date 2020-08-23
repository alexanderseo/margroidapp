from django.contrib import admin
from product.models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes.fields import GenericForeignKey
from .forms import ComplectForProductsForm


class PriceListFilter(admin.SimpleListFilter):
    title = 'Категория цен'
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Низкая цена: до 10000'),
            ('medium', 'Средняя цена: 10000-15000'),
            ('high', 'Высокая цена: от 15000'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=10000)
        elif self.value() == 'medium':
            return queryset.filter(price__gte=10000,
                                   price__lte=15000)
        elif self.value() == 'high':
            return queryset.filter(price__gt=15000)


class FotogaleryInline(admin.StackedInline):
    model = Fotogalery


class SizeInline(admin.StackedInline):
    model = Sizes


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class CategoryChildAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'on_sale', 'sale', 'price', 'new_price', 'in_stock', 'category')
    list_editable = ('price', 'sale',)
    search_fields = ('name',)
    list_filter = ('category', PriceListFilter,)
    list_select_related = False
    form = ComplectForProductsForm
    inlines = [FotogaleryInline, SizeInline]


class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'price',)


class SizesAdmin(admin.ModelAdmin):
    list_display = ('product', 'id', 'get_size', 'price', 'saleprice',)
    search_fields = ('id',)
    ordering = ('id',)
    list_editable = ('price',)

    def get_size(self, obj):
        return "{0}*{1}".format(obj.height, obj.width)

    get_size.short_description = 'Размер'


admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryChild, CategoryChildAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Sizes, SizesAdmin)
admin.site.register(Colors, ColorAdmin)
