from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse


class CartAdd(View):
    """
    Добавить в корзину
    """
    def get(self, request):
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


class CartPage(View):
    """
    Корзина
    """
    def get(self, request):
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


class ComplectToCart(View):
    """
    Комплект в корзину
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request, was_item_added=True)
        post_dict = dict(request.POST)
        del post_dict['csrfmiddlewaretoken']
        for key, value in post_dict.items():
            complect_item = Product.objects.get(id=key)
            complect_item_count = int(value[0])
            complect_item_clear = Sizes.objects.get(product=complect_item)
            cart.add_to_cart(complect_item_clear, default_count=complect_item_count)
        return JsonResponse({'total': len(cart.products.all())})
