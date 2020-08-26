from django.shortcuts import render, reverse
from django.views.generic.base import View
from auth.forms import LoginForm, AccountCreationForm
from product.models import ShopUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail


class AuthPage(View):
    """
    Авторизация
    """
    def get(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if '@' in username:
                username = User.objects.get(email=username)
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('base_view'))
        context = {
            'form': form
        }
        return render(request, 'auth/login.html', context)


class RegistrationView(View):
    """
    Регистрация
    """
    def get(self, request):
        form = AccountCreationForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            new_user = form.save(commit=False)
            try:
                validate_password(password, new_user)
                new_user.set_password(password)
                new_user.save()
                ShopUser.objects.create(user=User.objects.get(username=username))
                new_user = authenticate(username=username, password=password)
                if new_user:
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('base_view'))
            except ValidationError as e:
                form.add_error('password', e)
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)


class SendFeedbackView(View):
    """
    Сообщение с сайта
    """
    def get(self, request):
        name = request.POST.get('name')
        email_from = request.POST.get('email_from')
        message = request.POST.get('message')
        send_mail("Новое сообщение от margroid-msk.ru", "{0}.\nОт {1} ({2})".format(message, email_from, name),
                  settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
        return JsonResponse({})
