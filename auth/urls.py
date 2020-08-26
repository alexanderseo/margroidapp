from django.urls import path, reverse_lazy
from auth.views import AuthPage, RegistrationView, SendFeedbackView
from django.contrib.auth.views import LogoutView

app_name = 'auth'


urlpatterns = [
    path('login/', AuthPage.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home:home-page')), name='logout_view'),
    path('registration/', RegistrationView.as_view(), name='registration_view'),
    path('send-feedback/', SendFeedbackView.as_view(), name='send_feedback_view'),
]
