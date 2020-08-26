from django.urls import path
from product.views import *

app_name = 'product'


urlpatterns = [
    path('<slug:product_id>/', ProductPage.as_view(), name='product-page'),
    path('<slug:category_slug>/<subcategory_slug>/', SubCategoryPage.as_view(), name='subcategory_detail_view'),
    path('<slug:category_slug>/', CategoryPage.as_view(), name='category_detail_view'),
    path('inc-product-count/', IncreaseProductCountView.as_view(), name='increase_product_count_view'),
    path('dec-product-count/', DecreaseProductCountView.as_view(), name='decrease_product_count_view'),
    path('select-product-color/', SelectProductColorView.as_view(), name='select_product_color_view'),
    path('add-comment/<slug:product_id>/', AddCommentView.as_view(), name='add_comment_view'),
    # path(r'^add-complect-to-cart/$', add_complect_to_cart_view, name='add_complect_to_cart_view'),
    # path(r'^add-to-cart/$', add_to_cart_view, name='add_to_cart_view'),
    # path(r'^remove-from-cart/$', remove_from_cart_view, name='remove_from_cart_view'),

    # path(r'^product/(?P<product_id>\d+)/$', product_detail_view, name='product_detail_view'),
]
