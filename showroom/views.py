from django.shortcuts import render
from django.views.generic.base import View
from utils.functions_products_cart import get_watched_products
from product.models import Product, Category
from showroom.models import ShowRoomModel


class ShowRoomPage(View):
    """
    Вывод данных страницу Шоу-рум
    """
    def get(self, request):
        cart, cart_objects_count = get_users_cart(request)
        categories = Category.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)[:4]
        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0
        meta_info = ShowRoomModel.objects.all()
        context = {
            'categories': categories,
            'products_on_sale': products_on_sale,
            'watched_products': get_watched_products(request.session.get('watched_products', None)),
            'comparison_list': compare_list_count,
            'cart_items_count': cart_objects_count,
            'showroom_title': meta_info.meta_title,
            'showroom_description': meta_info.meta_description
        }
        return render(request, 'showroom/showroom.html', context)
