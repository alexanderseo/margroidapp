from django.shortcuts import render
from django.views.generic.base import View
from utils.functions_products_cart import *


class ComparePage(View):
    """
    Страница сравнения
    """
    def get(self, request):
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
        return render(request, 'compare/compare.html', context)


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
