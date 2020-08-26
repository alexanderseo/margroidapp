from django.template.defaulttags import register
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from product.models import *


@register.filter
def get_item(dictionary, key):
    """
    Пока не понял для чего
    """
    return dictionary.get(key)


def set_paginator(items, items_per_page, curr_page):
    """
    Пагинация
    """
    paginator = Paginator(items, items_per_page)
    result_page_items = paginator.get_page(curr_page)
    return result_page_items


def get_next_paginator_page(current_page, num_pages):
    """
    Пагинация
    """
    if current_page is None:
        return '2'
    else:
        return current_page if int(current_page) == num_pages else str(int(current_page) + 1)


def get_prev_paginator_page(current_page):
    """
    Пагинация
    """
    result_page = '1' if current_page == '1' or current_page is None else str(int(current_page) - 1)
    return result_page


def get_GET_params(get_dict):
    """
    Пока не понял для чего
    """
    get_copy = get_dict.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    return parameters


def get_users_cart(request, was_item_added=False):
    """
    Что-то с корзиной товаров
    """
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.products.count()
    except:
        if not was_item_added:
            return (None, 0)
        else:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            request.session['cart_id'] = cart_id
            cart = Cart.objects.get(id=cart_id)
    return (cart, len(cart.products.all()))


def sort_products_by_query(query, products, sort_queries):
    """
    Сортировка товаров
    """
    if query == 'price-asc':
        sort_queries.append('price-asc')
        products = products.order_by('price')
    elif query == 'price-desc':
        sort_queries.append('price-desc')
        products = products.order_by('-price')
    elif query == 'name-asc':
        sort_queries.append('name-asc')
        products = products.order_by('name')
    elif query == 'name-desc':
        sort_queries.append('name-desc')
        products = products.order_by('-name')
    return products


def get_watched_products(session_list):
    """
    Вывод просмотренных товаров
    """
    if session_list is None:
        return None
    result = []
    for product_id in session_list:
        product = Product.objects.get(id=int(product_id))
        result.append(product)
    return result


def get_min_size_colors(product, colors):
    """
    Функция получния цветов для размеров,
    Сейчас она не нужна, но используется
    """
    heights = []
    widths = []
    for color in colors:
        heights.append(color.product.height)
        widths.append(color.product.width)
    min_height = min(heights)
    min_width = min(widths)
    size = Sizes.objects.get(product=product, height=min_height, width=min_width)
    min_size_colors = ProductColorsSizes.objects.filter(product=size)
    return min_size_colors


def remove_duplicates_colors(lst):
    """
    Что-то с цветом
    """
    return list(dict.fromkeys(lst))


def find_extremum_prices(products):
    """
    Что-то с ценой
    """
    all_prices = []
    for obj in products:
        if obj.on_sale:
            all_prices.append(obj.new_price)
        else:
            all_prices.append(obj.price)
    return (min(all_prices), max(all_prices))


def remove_from_cart_view(request):
    """
    Очистить корзину
    """
    cart, cart_objects_count = get_users_cart(request)
    product_id = request.GET.get('cart-item')
    product = Sizes.objects.get(id=product_id)
    cart.remove_from_cart(product)
    return HttpResponseRedirect(reverse('cart_view'))

