from django.shortcuts import render
from django.views.generic.base import View
from product.models import Product, Category, CategoryChild
from utils.functions_products_cart import *
from slugify import slugify
from openpyxl import Workbook


class PriceListPage(View):
    """
    Страница прайс-лист
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request)
        categories = Category.objects.all()
        subcategories = CategoryChild.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)[:4]
        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0
        context = {}
        context['categories'] = categories
        context['subcategories'] = subcategories
        context['products_on_sale'] = products_on_sale
        context['comparison_list'] = compare_list_count
        context['cart_items_count'] = cart_objects_count

        if not request.GET:
            products = Product.objects.all()
            request.session['category_to_print'] = 'Все категории'
            context['selected_category'] = 'Все категории'
            context['selected_category_to_print'] = slugify(context['selected_category'])
            context['products'] = products

            wb = Workbook()
            ws = wb.active
            ws.title = 'Выгрузка товара'

            for product in products:
                ws.append([product.name, product.new_price])
                sizes = Sizes.objects.filter(product=product)
                if sizes:
                    for size in sizes:
                        product_size = "{0}*{1}".format(size.height, size.width)
                        ws.append([product.name + "(" + product_size + ")", size.price])
            wb.save("media/report.xlsx")
        else:
            request.session['category_to_print'] = request.GET.get('selected-category')
            context['selected_category'] = request.GET.get('selected-category')
            context['selected_category_to_print'] = slugify(context['selected_category'])
            if request.GET.get('selected-category') == 'Все категории':
                products = Product.objects.all()
                context['products'] = products
                return render(request, 'pricelist/price-list.html', context)
            if not '/' in request.GET.get('selected-category'):
                category_selected = Category.objects.get(name=request.GET.get('selected-category'))
                context['products'] = Product.objects.filter(category=category_selected)
                return render(request, 'pricelist/price-list.html', context)

            full_category_name = request.GET.get('selected-category')
            category_selected = Category.objects.get(name=full_category_name.split('/')[0].strip())
            subcategory_selected = CategoryChild.objects.get(name=full_category_name.split('/')[1].strip())
            context['products'] = Product.objects.filter(category=category_selected, sub_category=subcategory_selected)

        context['watched_products'] = get_watched_products(request.session.get('watched_products', None))
        return render(request, 'pricelist/price-list.html', context)


class PriceListPrint(View):
    """
    Печать прайс-листа
    """
    def get(self, request, slug):
        if slug == 'vse-kategorii':
            products = Product.objects.all()
        elif slug == 'Komplektuiushchie':
            products = Product.objects.filter(category__name='Комплектующие')
        else:
            full_category_name = request.session.get('category_to_print')
            category_selected = Category.objects.get(name=full_category_name.split('/')[0].strip())
            subcategory_selected = CategoryChild.objects.get(name=full_category_name.split('/')[1].strip())
            products = Product.objects.filter(category=category_selected, sub_category=subcategory_selected)
        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0
        context = {
            'products': products,
            'category': request.session['category_to_print'],
            'comparison_list': compare_list_count
        }
        return render(request, 'pricelist/pricelist_print.html', context)
