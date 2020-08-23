from django.shortcuts import render, reverse
from django.template.response import TemplateResponse
from itertools import chain
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from django.template.defaulttags import register
from slugify import slugify
from django.core.paginator import Paginator
from .models import *
from .forms import *
from django.conf import settings
from openpyxl import Workbook
from collections import deque, defaultdict
from django.contrib.auth.models import User
from django.db.models import F
import json
import collections


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def set_paginator(items, items_per_page, curr_page):
    paginator = Paginator(items, items_per_page)
    result_page_items = paginator.get_page(curr_page)
    return result_page_items


def get_next_paginator_page(current_page, num_pages):
    if current_page is None:
        return '2'
    else:
        return current_page if int(current_page) == num_pages else str(int(current_page) + 1)


def get_prev_paginator_page(current_page):
    result_page = '1' if current_page == '1' or current_page is None else str(int(current_page) - 1)
    return result_page


def get_GET_params(get_dict):
    get_copy = get_dict.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    return parameters


def base_view(request):
    contact_form = ContactForm(request.POST or None)
    product_categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)
    news = News.objects.all()[:3]
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    cart, cart_objects_count = get_users_cart(request)
    meta_info = Pages.objects.get(related_page='Главная')
    context = {
        'categories': product_categories,
        'products_on_sale': products_on_sale,
        'news': news,
        'contact_form': contact_form,
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'main_title': meta_info.meta_title,
        'main_description': meta_info.meta_description
    }
    return render(request, 'index.html', context)


def get_watched_products(session_list):
    if session_list is None:
        return None
    result = []
    for product_id in session_list:
        product = Product.objects.get(id=int(product_id))
        result.append(product)
    return result


def add_comment_view(request, product_id):
    current_product = Product.objects.get(id=product_id)
    comment_text = request.POST.get('comment')
    current_user = ShopUser.objects.get(user=request.user)
    Comment.objects.create(product=current_product, user=current_user, body=comment_text)
    return HttpResponseRedirect(reverse('product_detail_view', kwargs={'product_id': product_id}))


def get_min_size_colors(product, colors):
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


def product_detail_view(request, product_id):
    current_product = Product.objects.get(id=product_id)
    current_product_sizes = Sizes.objects.filter(product=current_product).order_by('height', 'width')
    watched_products = request.session.get('watched_products', default=None)
    if watched_products is None:
        watch_list_products = deque()
        watch_list_products.append(current_product.id)
        request.session['watched_products'] = list(collections.deque(watch_list_products))
    else:
        if len(request.session['watched_products']) < 4:
            watch_list_products = deque(request.session['watched_products'])
            if not current_product.id in watch_list_products:
                watch_list_products.append(current_product.id)
                request.session['watched_products'] = list(collections.deque(watch_list_products))
        else:
            watch_list_products = deque(request.session['watched_products'])
            if not current_product.id in watch_list_products:
                watch_list_products.popleft()
                watch_list_products.append(current_product.id)
                request.session['watched_products'] = list(collections.deque(watch_list_products))

    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:3]
    comments = Comment.objects.filter(product=current_product).order_by('-created_on')
    colors = ProductColorsSizes.objects.filter(product__in=current_product_sizes)
    if not 'Комплектующие' in current_product.category.name:
        min_colors = get_min_size_colors(current_product, colors)
    else:
        min_colors = []
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    cart, cart_objects_count = get_users_cart(request)
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'current_product': current_product,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comments': comments,
        'colors': colors,
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'current_product_sizes': current_product_sizes,
        'min_colors': min_colors
    }
    return render(request, 'product_detail.html', context)


def find_extremum_prices(products):
    all_prices = []
    for obj in products:
        if obj.on_sale:
            all_prices.append(obj.new_price)
        else:
            all_prices.append(obj.price)
    return (min(all_prices), max(all_prices))


def sort_products_by_query(query, products, sort_queries):
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


def subcategory_detail_view(request, category_slug, subcategory_slug):
    cart, cart_objects_count = get_users_cart(request)
    sort_query = request.GET.get('sort', None)
    current_page = request.GET.get('page')
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    current_category = Category.objects.get(slug=category_slug)
    current_subcategory = CategoryType.objects.get(slug=subcategory_slug)

    if request.GET:
        if request.GET.get('from') and request.GET.get('to'):
            from_price = int(request.GET.get('from'))
            to_price = int(request.GET.get('to'))
            products = Product.objects.filter(category=current_category, \
                                              sub_category=current_subcategory, price__lte=to_price,
                                              price__gte=from_price)
        else:
            products = Product.objects.filter(category=current_category, sub_category=current_subcategory)
    else:
        products = Product.objects.filter(category=current_category, sub_category=current_subcategory)

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
        'current_subcategory': current_subcategory,
        'products': set_paginator(products, 10, current_page),
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

    return render(request, 'subcategory_detail.html', context)


def components_view(request):
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

    return render(request, 'subcategory_detail.html', context)


def category_detail_view(request, slug):
    cart, cart_objects_count = get_users_cart(request)
    if slug == 'komplektuyushie':
        category_products = Product.objects.filter(slug=slug)
    else:
        category_products = Category.objects.get(slug=slug)
    current_category = Category.objects.get(slug=slug)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'category_products': category_products,
        'current_category': current_category,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
    }
    return render(request, 'category_detail.html', context)


def search_view(request):
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
            filtered_subcategory = CategoryType.objects.get(name=subcategory_name)
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
    return render(request, 'search.html', context)


def detail_news_view(request, slug):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    current_news_item = News.objects.get(slug=slug)
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'current_news_item': current_news_item,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
    }
    return render(request, 'detail_news.html', context)


def news_view(request):
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    news = News.objects.all()
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'news': news,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count
    }
    return render(request, 'news.html', context)


def print_pricelist_view(request, slug):
    if slug == 'vse-kategorii':
        products = Product.objects.all()
    elif slug == 'Komplektuiushchie':
        products = Product.objects.filter(category__name='Комплектующие')
    else:
        full_category_name = request.session.get('category_to_print')
        category_selected = Category.objects.get(name=full_category_name.split('/')[0].strip())
        subcategory_selected = CategoryType.objects.get(name=full_category_name.split('/')[1].strip())
        products = Product.objects.filter(category=category_selected, sub_category=subcategory_selected)
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'products': products,
        'category': request.session['category_to_print'],
        'comparison_list': compare_list_count
    }
    return render(request, 'pricelist_print.html', context)


def pricelist_view(request, *args, **kwargs):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    subcategories = CategoryType.objects.all()
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
            return render(request, 'price-list.html', context)
        if not '/' in request.GET.get('selected-category'):
            category_selected = Category.objects.get(name=request.GET.get('selected-category'))
            context['products'] = Product.objects.filter(category=category_selected)
            return render(request, 'price-list.html', context)

        full_category_name = request.GET.get('selected-category')
        category_selected = Category.objects.get(name=full_category_name.split('/')[0].strip())
        subcategory_selected = CategoryType.objects.get(name=full_category_name.split('/')[1].strip())
        context['products'] = Product.objects.filter(category=category_selected, sub_category=subcategory_selected)

    context['watched_products'] = get_watched_products(request.session.get('watched_products', None))
    return render(request, 'price-list.html', context)


def delivery_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    delivery_types = DeliveryType.objects.all()
    meta_info = Pages.objects.get(related_page='Доставка')
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'delivery_types': delivery_types,
        'delivery_title': meta_info.meta_title,
        'delivery_description': meta_info.meta_description
    }
    return render(request, 'delivery.html', context)


def delete_from_comparison_view(request):
    current_product = request.POST.get('product-id')
    comparison_list = request.session.get('comparison_list')
    comparison_list.remove(current_product)
    request.session['comparison_list'] = comparison_list
    return HttpResponseRedirect(reverse('compare_view'))


def showroom_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    meta_info = Pages.objects.get(related_page='ShowRoom')
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'showroom_title': meta_info.meta_title,
        'showroom_description': meta_info.meta_description
    }
    return render(request, 'showroom.html', context)


def get_users_cart(request, was_item_added=False):
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


def add_to_cart_view(request):
    cart, cart_objects_count = get_users_cart(request, was_item_added=True)
    product_id = request.POST.get('product_id')
    color_id = request.POST.get('color_id', None)
    if not color_id is None:
        color = ProductColorsSizes.objects.get(id=color_id)
    else:
        color = None
    product = Sizes.objects.get(id=product_id)
    cart.add_to_cart(product, color)
    return JsonResponse({'total': cart.products.count()})


def increase_product_count_view(request):
    cart, cart_objects_count = get_users_cart(request)
    cart_item_id = request.GET.get('item-id')
    cart_item = cart.products.get(id=cart_item_id)
    cart_item.count += 1
    if cart_item.color:
        cart_item.total_price += cart_item.price_per_item_color
        cart.total_price += cart_item.price_per_item_color
    else:
        cart_item.total_price += cart_item.product.price
        cart.total_price += cart_item.product.price
    cart_item.save()
    cart.save()
    return HttpResponseRedirect(reverse('cart_view'))


def decrease_product_count_view(request):
    cart, cart_objects_count = get_users_cart(request)
    cart_item_id = request.GET.get('item-id')
    cart_item = cart.products.get(id=cart_item_id)
    if cart_item.count != 1:
        cart_item.count -= 1
        if cart_item.color:
            cart_item.total_price -= cart_item.price_per_item_color
            cart.total_price -= cart_item.price_per_item_color
        else:
            cart_item.total_price -= cart_item.product.price
            cart.total_price -= cart_item.product.price
        cart_item.save()
        cart.save()
    return HttpResponseRedirect(reverse('cart_view'))


def remove_from_cart_view(request):
    cart, cart_objects_count = get_users_cart(request)
    product_id = request.GET.get('cart-item')
    product = Sizes.objects.get(id=product_id)
    cart.remove_from_cart(product)
    return HttpResponseRedirect(reverse('cart_view'))


def select_product_color_view(request):
    product_size_id = request.POST.get('product_size_id')
    product_size = Sizes.objects.get(id=product_size_id)
    product_colors_sizes = ProductColorsSizes.objects.filter(product=product_size)
    result_sizes = defaultdict()
    for color_size in product_colors_sizes:
        lst = []
        lst.append(color_size.color.image.url)
        lst.append(color_size.product.height)
        lst.append(color_size.product.width)
        lst.append(color_size.price)
        lst.append(color_size.product.price)
        lst.append(color_size.id)
        result_sizes[color_size.id] = lst
    return JsonResponse({'colors': result_sizes})


def cart_view(request):
    if request.user.is_authenticated:
        current_user = ShopUser.objects.get(user=request.user)
    else:
        current_user = None
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    cart, cart_objects_count = get_users_cart(request)
    if not cart is None:
        price_with_discount = cart.total_price
        delivery_cost = 0 if price_with_discount >= 20000 else 500
        standart_sale = StandartSale.objects.first().sale if price_with_discount >= 20000 else 0
        personal_sale = 0 if not request.user.is_authenticated else current_user.discount
        price_with_standart_discount = int(price_with_discount * (1 - standart_sale / 100))
        price_with_personal_discount = int(price_with_standart_discount * (1 - personal_sale / 100))
        result_price = price_with_personal_discount + delivery_cost
    else:
        result_price = 0
        standart_sale = 0
    categories = Category.objects.all()
    meta_info = Pages.objects.get(related_page='Корзина')
    context = {
        'cart': cart,
        'orders_state': 'false',
        'personal_data_state': 'false',
        'cart_state': 'true',
        'compare_state': 'false',
        'cart_items_count': cart_objects_count,
        'comparison_list': compare_list_count,
        'current_user': current_user,
        'categories': categories,
        'price_with_discount': result_price,
        'standart_sale': standart_sale,
        'cart_title': meta_info.meta_title,
        'cart_description': meta_info.meta_description
    }
    return render(request, 'cart.html', context)


def add_complect_to_cart_view(request):
    cart, cart_objects_count = get_users_cart(request, was_item_added=True)
    post_dict = dict(request.POST)
    del post_dict['csrfmiddlewaretoken']
    for key, value in post_dict.items():
        complect_item = Product.objects.get(id=key)
        complect_item_count = int(value[0])
        complect_item_clear = Sizes.objects.get(product=complect_item)
        cart.add_to_cart(complect_item_clear, default_count=complect_item_count)
    return JsonResponse({'total': len(cart.products.all())})


def add_to_comparison_view(request):
    comparison_list = request.session.get('comparison_list', [])
    comparison_list.append(request.POST.get('product_id'))
    request.session['comparison_list'] = comparison_list
    return JsonResponse({'total_comparison': len(comparison_list)})


def generate_comparison_dict(ids):
    result = {}
    if len(ids) == 1:
        result[ids[0]] = 4
    elif len(ids) == 2:
        result[ids[0]] = 2
        result[ids[1]] = 2
    elif len(ids) == 3:
        result[ids[0]] = 2
        result[ids[1]] = 1
        result[ids[2]] = 1
    else:
        for ind in range(len(ids)):
            result[ids[ind]] = 1
    return result


def remove_duplicates_colors(lst):
    return list(dict.fromkeys(lst))


def compare_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    comparison_list = request.session.get('comparison_list', [])
    ids = [int(i) for i in comparison_list]
    comparison_list_products = Product.objects.filter(id__in=ids)
    all_sizes_objects = Sizes.objects.filter(product__in=comparison_list_products)
    sizes_count_raw = [i.product.id for i in all_sizes_objects]
    sizes_count_clear = {}
    for size_id in sizes_count_raw:
        sizes_count_clear[size_id] = sizes_count_raw.count(size_id)
    comparison_dict = generate_comparison_dict(ids)
    all_colors_objects = ProductColorsSizes.objects.filter(product__in=all_sizes_objects)
    product_colors_clear = defaultdict(list)
    for color in all_colors_objects:
        product_colors_clear[color.product.product.id].append(color.color.name)
    for color in all_colors_objects:
        clear_lst = remove_duplicates_colors(product_colors_clear[color.product.product.id])
        product_colors_clear[color.product.product.id] = clear_lst
    meta_info = Pages.objects.get(related_page='Сравнение')
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list_products': comparison_list_products,
        'comparison_dict': comparison_dict,
        'comparison_list': len(comparison_list_products),
        'sizes_count': sizes_count_clear,
        'products_colors': product_colors_clear,
        'personal_data_state': 'false',
        'cart_state': 'false',
        'compare_state': 'true',
        'orders_state': 'false',
        'cart_items_count': cart_objects_count,
        'compare_title': meta_info.meta_title,
        'compare_description': meta_info.meta_description
    }
    return render(request, 'compare.html', context)


@login_required(login_url='/login/')
def orders_view(request):
    cart, cart_objects_count = get_users_cart(request)
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    current_user = ShopUser.objects.get(user=request.user)
    orders = Order.objects.filter(user=current_user)
    orders_info_dict = defaultdict()
    orders_info_count = {}
    for order in orders:
        products = OrderItems.objects.filter(order=order)
        orders_info_dict[order.id] = products
        orders_info_count[order.id] = products.count()
    context = {
        'personal_data_state': 'false',
        'cart_state': 'false',
        'compare_state': 'false',
        'orders_state': 'true',
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'orders': orders,
        'orders_info': orders_info_dict,
        'orders_info_count': orders_info_count
    }
    return render(request, 'orders.html', context)


def save_profile_info_view(request):
    current_user = ShopUser.objects.get(user=request.user)
    username = request.POST.get('profile-username', None)
    if not username is None:
        current_user.user.username = username
    first_name = request.POST.get('profile-name', None)
    if not first_name is None:
        current_user.user.first_name = first_name
    email = request.POST.get('profile-email', None)
    if not email is None:
        current_user.user.email = email
    phone_number = request.POST.get('profile-phone', None)
    if not phone_number is None:
        current_user.phone_number = phone_number
    current_user.user.save()
    current_user.save()
    return HttpResponseRedirect(reverse('profile_view'))


@login_required(login_url='/login/')
def profile_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    current_user = ShopUser.objects.get(user=request.user)
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'categories': categories,
        'current_user': current_user,
        'comparison_list': compare_list_count,
        'personal_data_state': 'true',
        'cart_state': 'false',
        'compare_state': 'false',
        'orders_state': 'false',
        'cart_items_count': cart_objects_count,
    }
    return render(request, 'profile.html', context)


def send_user_data(username, password, email):
    subject = 'TDVELS - данные для входа'
    body = "Для входа на сайт используйте логин: {0} или почту, пароль: {1}".format(username, password)
    send_mail(subject, body, settings.EMAIL_HOST_USER, [email])


def make_order_view(request):
    cart, cart_objects_count = get_users_cart(request)
    total_cart_price = request.POST.get('total-cart-price')
    first_name = request.POST.get('first-name')
    email = request.POST.get('email')
    delivery_type = request.POST.get('delivery-type-radios')
    full_names = [request.POST.get('full-name-1'), request.POST.get('full-name-2'),
                  request.POST.get('full-name-3'), request.POST.get('full-name-4')]
    phones = [request.POST.get('phone-1'), request.POST.get('phone-2'),
              request.POST.get('phone-3'), request.POST.get('phone-4')]
    delivery_deadlines = [request.POST.get('delivery-deadline-1'), request.POST.get('delivery-deadline-2')]
    additional_informations = [request.POST.get('additional-information-1'),
                               request.POST.get('additional-information-2'),
                               request.POST.get('additional-information-3'),
                               request.POST.get('additional-information-4')]
    region = request.POST.get('region')
    city = request.POST.get('city')
    street = request.POST.get('street')
    house_number = request.POST.get('house-number')
    padik = request.POST.get('padik')
    flat_number = request.POST.get('flat-number')
    payment_type = request.POST.get('payment-type')
    org_name = request.POST.get('org-name')
    inn = request.POST.get('inn')
    legal_address = request.POST.get('legal-address')

    full_name = [x for x in full_names if x != '']
    phone = [x for x in phones if x != '']
    deadline = [x for x in delivery_deadlines if x != '']
    info = [x for x in additional_informations if x != '']
    full_name = full_name[0] if len(full_name) > 0 else None
    phone = phone[0] if len(phone) > 0 else None
    deadline = deadline[0] if len(deadline) > 0 else None
    info = info[0] if len(info) > 0 else None

    if house_number == '':
        house_number = None
    if padik == '':
        padik = None
    if flat_number == '':
        flat_number = None
    if request.user.is_authenticated:
        user = ShopUser.objects.get(user=request.user)
    else:
        if User.objects.filter(email=email).exists():
            founded_user = User.objects.get(email=email)
            user = ShopUser.objects.get(user=founded_user)
        else:
            password = User.objects.make_random_password()
            new_user = User.objects.create(first_name=first_name, email=email)
            new_user.set_password(password)
            username = '{0}{1}'.format('unknown_user_', new_user.id)
            new_user.username = username
            new_user.save()
            user = ShopUser.objects.create(user=new_user)
            send_user_data(username, password, email)

    new_order = Order.objects.create(user=user, name=first_name, full_name=full_name, phone=phone, email=email,
                                     additional_information=info, delivery_type=delivery_type, delivery_region=region,
                                     delivery_city=city, delivery_street=street, delivery_house=house_number,
                                     delivery_padik=padik,
                                     delivery_flat=flat_number, total_price=total_cart_price,
                                     delivery_deadline=deadline,
                                     payment_type=payment_type, org_name=org_name, inn=inn, legal_address=legal_address)

    for cart_item in cart.products.all():
        OrderItems.objects.create(order=new_order, product=cart_item.product, count=cart_item.count,
                                  color=cart_item.color, total_price=cart_item.total_price)

    return HttpResponseRedirect(reverse('base_view'))


def registration_view(request):
    form = AccountCreationForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        new_user = form.save(commit=False)
        try:
            validate_password(password, new_user)
            new_user.set_password(password)
            new_user.save()
            ShopUser.objects.create(user=User.objects.get(username=username))
            new_user = authenticate(username=username, password=password)
            if new_user:
                login(request, new_user)
                return HttpResponseRedirect(reverse('base_view'))
        except ValidationError as e:
            form.add_error('password', e)
    context = {
        'form': form
    }
    return render(request, 'registration.html', context)


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        if '@' in username:
            username = User.objects.get(email=username)
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('base_view'))
    context = {
        'form': form
    }
    return render(request, 'login.html', context)


def send_feedback_view(request):
    name = request.POST.get('name')
    email_from = request.POST.get('email_from')
    message = request.POST.get('message')
    send_mail("Новое сообщение от margroid-msk.ru", "{0}.\nОт {1} ({2})".format(message, email_from, name),
              settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
    return JsonResponse({})