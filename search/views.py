from django.shortcuts import render
from django.views.generic.base import View
from utils.functions_products_cart import get_watched_products, set_paginator, get_prev_paginator_page, get_next_paginator_page, get_GET_params
from product.models import *


class SearchPage(View):
    """
    Страница поиска
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request)
        searching_query = request.GET.get('q')
        current_page = request.GET.get('page')
        if 'category' in request.GET:
            searching_category = request.GET.get('category')
            selected_category_filter = searching_category
            if searching_category == 'Все категории':
                founded_products = Product.objects.filter(name__icontains=searching_query)
            elif searching_category == 'Комплектующие':
                filtered_category = Category.objects.get(name='Комплектующие')
                founded_products = Product.objects.filter(name__icontains=searching_query, category=filtered_category)
            else:
                category_name = searching_category.split('/')[0].strip()
                subcategory_name = searching_category.split('/')[1].strip()
                filtered_category = Category.objects.get(name=category_name)
                filtered_subcategory = CategoryChild.objects.get(name=subcategory_name)
                founded_products = Product.objects.filter(name__icontains=searching_query, category=filtered_category,
                                                          sub_category=filtered_subcategory)
        else:
            selected_category_filter = 'Все категории'
            founded_products = Product.objects.filter(name__icontains=searching_query)

        categories = Category.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)[:4]
        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0
        context = {
            'categories': categories,
            'products_on_sale': products_on_sale,
            'query': searching_query,
            'comparison_list': compare_list_count,
            'cart_items_count': cart_objects_count,
        }
        context['founded_products'] = set_paginator(founded_products, 6, current_page)
        context['prev_page'] = get_prev_paginator_page(current_page)
        context['next_page'] = get_next_paginator_page(current_page, context['founded_products'].paginator.num_pages)
        parameters = get_GET_params(request.GET)
        context['parameters'] = parameters
        context['selected_category_filter'] = selected_category_filter
        context['watched_products'] = get_watched_products(request.session.get('watched_products', None))
        return render(request, 'search/search.html', context)
