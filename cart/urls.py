from django.urls import path
from cart.views import *

app_name = 'cart'

urlpatterns = [
    path('add-complect-to-cart/', ComplectToCart.as_view(), name='add_complect_to_cart_view'),
    path('add-to-cart/', CartAdd.as_view(), name='add_to_cart_view'),
    path('remove-from-cart/', remove_from_cart_view, name='remove_from_cart_view'),
    path('', CartPage.as_view(), name='cart_view'),

    # path(r'^product/(?P<product_id>\d+)/$', product_detail_view, name='product_detail_view'),
]