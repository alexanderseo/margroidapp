from django.urls import path
from product.views import ProductPage, CategoryPage, SubCategoryPage

app_name = 'product'


urlpatterns = [
    path('<slug:product_id>/', ProductPage.as_view(), name='product-page'),
    path('<slug:category_slug>/<subcategory_slug>/', SubCategoryPage.as_view(), name='subcategory_detail_view'),
    path('<slug:category_slug>/', CategoryPage.as_view(), name='category_detail_view'),
    # path(r'^inc-product-count/$', increase_product_count_view, name='increase_product_count_view'),
    # path(r'^dec-product-count/$', decrease_product_count_view, name='decrease_product_count_view'),
    # path(r'^select-product-color/$', select_product_color_view, name='select_product_color_view'),
    # path(r'^add-complect-to-cart/$', add_complect_to_cart_view, name='add_complect_to_cart_view'),
    # path(r'^add-to-cart/$', add_to_cart_view, name='add_to_cart_view'),
    # path(r'^remove-from-cart/$', remove_from_cart_view, name='remove_from_cart_view'),
    # path(r'^components/$', components_view, name='components_view'),
    # path(r'^add-comment/(?P<product_id>\d+)/$', add_comment_view, name='add_comment_view'),
    # path(r'^product/(?P<product_id>\d+)/$', product_detail_view, name='product_detail_view'),
]
