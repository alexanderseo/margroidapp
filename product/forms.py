from django import forms
from product.models import Product


class ComplectForProductsForm(forms.ModelForm):
    complect = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(category__name='Комплектующие'),
        label='Комплектующие',
        required=False)
