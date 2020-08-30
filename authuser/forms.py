from django import forms
from django.contrib.auth.models import User
from product.models import Product


class ContactForm(forms.Form):
    """
    Форма обратной связи
    """
    name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    email = forms.EmailField(label='Почтовый ящик', widget=forms.TextInput(attrs={'placeholder': 'example@mail.ru'}))
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(
        attrs={'placeholder': 'Напишите свое сообщение и мы обязательно Вам поможем!'}))


class ResetPasswordForm(forms.Form):
    """
    Сбросить пароль
    """
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Почтовый ящик'}), label='')

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)


class LoginForm(forms.Form):
    """
    Авторизация
    """
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Логин или email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=username).exists():
            raise forms.ValidationError("User with this username doesnt exist.")
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            user = User.objects.get(email=username)
        if not user.check_password(password):
            raise forms.ValidationError("Invalid password.")


class AccountCreationForm(forms.ModelForm):
    """
    Создание аккаунта
    """
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Почтовый ящик'}), label='')
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='')
    password_check = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), label='')

    class Meta:
        model = User
        fields = ('email', 'username', 'password',)

    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        password_check = self.cleaned_data.get('password_check')
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists.")
        if password != password_check:
            raise forms.ValidationError("Passwords dont match.")
        return cleaned_data


class ComplectForProductsForm(forms.ModelForm):
    """
    Комплектация
    """
    complect = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(
            category__name='Комплектующие'),
        label='Комплектующие', required=False)
