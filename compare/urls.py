from django.urls import path
from compare.views import *

app_name = 'compare'

urlpatterns = [
    path('add-to-comparison/', add_to_comparison_view, name='add_to_comparison_view'),
    path('delete-from-comparison/', delete_from_comparison_view, name='delete_from_comparison_view'),
    path('', ComparePage.as_view(), name='compare_view'),
]
