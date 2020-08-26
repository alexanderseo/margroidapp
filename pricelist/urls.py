from django.urls import path
from pricelist.views import PriceListPage, PriceListPrint

app_name = 'pricelist'


urlpatterns = [
    path('<slug>/', PriceListPrint.as_view(), name='print_pricelist_view'),
    path('', PriceListPage.as_view(), name='pricelist_view'),
]
