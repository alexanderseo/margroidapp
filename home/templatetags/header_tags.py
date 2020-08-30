from django import template
from home.models import Header, ContactBlockHomePage

register = template.Library()


@register.inclusion_tag('layouts/header.html')
def header_elements():
    header_elem = Header.objects.all()
    return {'header_elem': header_elem, }


@register.inclusion_tag('layouts/contact_block_middle_home_page.html')
def contact_elements():
    contact_block_middle = ContactBlockHomePage.objects.first()
    return {'contact_block_middle': contact_block_middle, }
