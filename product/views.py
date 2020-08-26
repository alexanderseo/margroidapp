from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from collections import deque, defaultdict
from product.models import *
import collections
from utils.functions_products_cart import *


class CategoryPage(View):
    """
    Вывод данных страницу основной категории
    """
    def get(self, request, slug):
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
        return render(request, 'product/category_detail.html', context)


class SubCategoryPage(View):
    """
        Вывод данных страницу подкатегории
        """
    def get(request, category_slug, subcategory_slug):
        cart, cart_objects_count = get_users_cart(request)
        sort_query = request.GET.get('sort', None)
        current_page = request.GET.get('page')
        categories = Category.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)[:4]
        current_category = Category.objects.get(slug=category_slug)
        current_subcategory = CategoryChild.objects.get(slug=subcategory_slug)

        if request.GET:
            if request.GET.get('from') and request.GET.get('to'):
                from_price = int(request.GET.get('from'))
                to_price = int(request.GET.get('to'))
                products = Product.objects.filter(
                    category=current_category,
                    sub_category=current_subcategory,
                    price__lte=to_price,
                    price__gte=from_price)
            else:
                products = Product.objects.filter(
                    category=current_category,
                    sub_category=current_subcategory)
        else:
            products = Product.objects.filter(
                category=current_category,
                sub_category=current_subcategory)

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
            'cart_items_count': cart_objects_count,
        }

        context['prev_page'] = get_prev_paginator_page(current_page)
        context['next_page'] = get_next_paginator_page(current_page, context['products'].paginator.num_pages)

        return render(request, 'product/subcategory_detail.html', context)


class ProductPage(View):
    """
    Вывод данных страницу товара
    """
    def get(self, request, product_id=None):
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
        return render(request, 'product/product_detail.html', context)


class IncreaseProductCountView(View):
    """
    Увеличение количество товара в корзине
    """
    def get(self, request):
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


class DecreaseProductCountView(View):
    """
    Уменьшение количества товара в корзине
    """
    def get(self, request):
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


class SelectProductColorView(View):
    """
    Выбор цвета товара
    """
    def get(self, request):
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


class AddCommentView(View):
    """
    Добавление комментария к товару
    """
    def get(self, request, product_id):
        current_product = Product.objects.get(id=product_id)
        comment_text = request.POST.get('comment')
        current_user = ShopUser.objects.get(user=request.user)
        Comment.objects.create(product=current_product, user=current_user, body=comment_text)
        return HttpResponseRedirect(reverse('product_detail_view', kwargs={'product_id': product_id}))
