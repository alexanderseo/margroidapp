from django.shortcuts import render
from django.views.generic.base import View
from home.models import SeoHomePage


class HomePage(View):
    """
    Вывод данных на главную
    """
    def get(self, request):
        contact_form = ContactForm(request.POST or None)
        product_categories = Category.objects.all()
        products_on_sale = Product.objects.filter(on_sale=True)
        news = News.objects.all()[:3]
        compare_list = request.session.get('comparison_list', 0)
        compare_list_count = len(compare_list) if compare_list else 0
        cart, cart_objects_count = get_users_cart(request)
        meta_info = Pages.objects.get(related_page='Главная')
        seo = SeoHomePage.objects.first()
        context = {
            'categories': product_categories,
            'products_on_sale': products_on_sale,
            'news': news,
            'contact_form': contact_form,
            'comparison_list': compare_list_count,
            'cart_items_count': cart_objects_count,
            'main_title': meta_info.meta_title,
            'main_description': meta_info.meta_description,
            'seo': seo,
        }
        return render(request, 'home/index.html', context)
