from django.shortcuts import render
from django.views.generic.base import View
from news.models import News
from product.models import Product, Category
from utils.functions_products_cart import get_watched_products, get_users_cart


class NewsPage(View):
    """
    Вывод всех новостей
    """
    def get(self, request):
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
        return render(request, 'news/news.html', context)


class DetailNewsPage(View):
    """
    Вывод одной новости
    """
    def get(self, request, slug):
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
        return render(request, 'news/detail_news.html', context)
