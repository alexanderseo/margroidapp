from django.shortcuts import render, reverse
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from authuser.models import ShopUser
from cart.models import *
from product.models import *
from utils.functions_products_cart import get_users_cart, send_user_data, get_watched_products
from collections import defaultdict


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
        seo = PageCartSeo.objects.first()
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
            'seo': seo,
        }
        return render(request, 'cart/cart.html', context)


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


class RemoveFromCartView(View):
    """
    Очистить корзину
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request)
        product_id = request.GET.get('cart-item')
        product = Sizes.objects.get(id=product_id)
        cart.remove_from_cart(product)
        return HttpResponseRedirect(reverse('cart:cart_view'))


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
    return render(request, 'cart/orders.html', context)


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

    return HttpResponseRedirect(reverse('home:home-page'))


def delivery_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    products_on_sale = Product.objects.filter(on_sale=True)[:4]
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    delivery_types = DeliveryType.objects.all()
    delivery_page = DeliveryPageSeo.objects.first()
    delivery_foto = delivery_page.fotosdelivery.all()
    context = {
        'categories': categories,
        'products_on_sale': products_on_sale,
        'watched_products': get_watched_products(request.session.get('watched_products', None)),
        'comparison_list': compare_list_count,
        'cart_items_count': cart_objects_count,
        'delivery_types': delivery_types,
        'delivery_page': delivery_page,
        'delivery_foto': delivery_foto,
    }
    return render(request, 'cart/delivery.html', context)
