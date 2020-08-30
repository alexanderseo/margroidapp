from django.urls import path
from cart.views import *

app_name = 'cart'

urlpatterns = [
    path('add-complect-to-cart/', ComplectToCart.as_view(), name='add_complect_to_cart_view'),
    path('add-to-cart/', CartAdd.as_view(), name='add_to_cart_view'),
    path('delivery/', delivery_view, name='delivery_view'),
    path('orders/', orders_view, name='orders_view'),
    path('make-order/', make_order_view, name='make_order_view'),
    path('remove-from-cart/', RemoveFromCartView.as_view(), name='remove_from_cart_view'),
    path('', CartPage.as_view(), name='cart_view'),
]
