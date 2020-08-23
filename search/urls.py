from django.urls import path
from search.views import SearchPage

app_name = 'search'


urlpatterns = [
    path('', SearchPage.as_view(), name='search_view'),
]
