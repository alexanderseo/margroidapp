from django import template
from home.models import Header

register = template.Library()


@register.inclusion_tag('layouts/header.html')
def header_elements():
    header_elem = Header.objects.all()
    return {'header_elem': header_elem, }
