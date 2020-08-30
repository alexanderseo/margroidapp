from django.shortcuts import render, reverse
from django.views.generic.base import View
from authuser.forms import LoginForm, AccountCreationForm
from product.models import ShopUser, Category
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail
from utils.functions_products_cart import get_users_cart


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


def save_profile_info_view(request):
    current_user = ShopUser.objects.get(user=request.user)
    username = request.POST.get('profile-username', None)
    if not username is None:
        current_user.user.username = username
    first_name = request.POST.get('profile-name', None)
    if not first_name is None:
        current_user.user.first_name = first_name
    email = request.POST.get('profile-email', None)
    if not email is None:
        current_user.user.email = email
    phone_number = request.POST.get('profile-phone', None)
    if not phone_number is None:
        current_user.phone_number = phone_number
    current_user.user.save()
    current_user.save()
    return HttpResponseRedirect(reverse('profile_view'))


@login_required(login_url='/login/')
def profile_view(request):
    cart, cart_objects_count = get_users_cart(request)
    categories = Category.objects.all()
    current_user = ShopUser.objects.get(user=request.user)
    compare_list = request.session.get('comparison_list', 0)
    compare_list_count = len(compare_list) if compare_list else 0
    context = {
        'categories': categories,
        'current_user': current_user,
        'comparison_list': compare_list_count,
        'personal_data_state': 'true',
        'cart_state': 'false',
        'compare_state': 'false',
        'orders_state': 'false',
        'cart_items_count': cart_objects_count,
    }
    return render(request, 'auth/profile.html', context)
