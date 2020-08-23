from django.urls import path
from showroom.views import ShowRoomPage

app_name = 'showroom'


urlpatterns = [
    path('', ShowRoomPage.as_view(), name='showroom_view'),
]
