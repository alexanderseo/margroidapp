from django.urls import path
from news.views import NewsPage, DetailNewsPage

app_name = 'news'


urlpatterns = [
    path('<slug>/', DetailNewsPage.as_view(), name='detail_news_view'),
    path('', NewsPage.as_view(), name='news_view'),
]
