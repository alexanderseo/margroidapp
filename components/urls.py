from django.urls import path
from components.views import ComponentsPage

app_name = 'components'


urlpatterns = [
    path('', ComponentsPage.as_view(), name='components_view'),
]