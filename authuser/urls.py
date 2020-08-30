from django.urls import path, reverse_lazy
from authuser.views import *
from django.contrib.auth.views import LogoutView

app_name = 'authuser'


urlpatterns = [
    path('login/', AuthPage.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home:home-page')), name='logout_view'),
    path('registration/', RegistrationView.as_view(), name='registration_view'),
    path('send-feedback/', SendFeedbackView.as_view(), name='send_feedback_view'),
    path('save-profile-info/', save_profile_info_view, name='save_profile_info_view'),
    path('profile/', profile_view, name='profile_view'),
]
