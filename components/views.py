from django.shortcuts import render
from django.views.generic.base import View
from product.models import Category, Product
from utils.functions_products_cart import *


class ComponentsPage(View):
    """
    Страница компонентов
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request)
        sort_query = request.GET.get('sort', None)
        current_page = request.GET.get('page')
        categories = Category.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)[:4]
        current_category = Category.objects.get(name='Комплектующие')

        if request.GET:
            if request.GET.get('from') and request.GET.get('to'):
                from_price = int(request.GET.get('from'))
                to_price = int(request.GET.get('to'))
                products = Product.objects.filter(category=current_category, price__lte=to_price, price__gte=from_price)
            else:
                products = Product.objects.filter(category=current_category)
        else:
            products = Product.objects.filter(category=current_category)

        extremum_prices = find_extremum_prices(products)
        parameters = get_GET_params(request.GET)

        sort_queries = []
        if not sort_query is None:
            products = sort_products_by_query(sort_query, products, sort_queries)

        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0

        context = {
            'categories': categories,
            'products_on_sale': products_on_sale,
            'current_category': current_category,
            'products': set_paginator(products, 6, current_page),
            'lowest_price': extremum_prices[0],
            'highest_price': extremum_prices[1],
            'parameters': parameters,
            'watched_products': get_watched_products(request.session.get('watched_products', None)),
            'sort_queries': sort_queries,
            'comparison_list': compare_list_count,
            'cart_items_count': cart_objects_count
        }

        context['prev_page'] = get_prev_paginator_page(current_page)
        context['next_page'] = get_next_paginator_page(current_page, context['products'].paginator.num_pages)

        return render(request, 'components/components.html', context)
