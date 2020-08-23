from django.urls import path
from home.views import HomePage

app_name = 'home'


urlpatterns = [
    path('', HomePage.as_view(), name='home-page'),
]
