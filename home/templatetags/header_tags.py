from django import template
from home.models import Header, ContactBlockHomePage, Slider
from news.models import News

register = template.Library()


@register.inclusion_tag('layouts/header.html')
def header_elements():
    header_elem = Header.objects.all()
    return {'header_elem': header_elem, }


@register.inclusion_tag('layouts/contact_block_middle_home_page.html')
def contact_elements():
    contact_block_middle = ContactBlockHomePage.objects.first()
    return {'contact_block_middle': contact_block_middle, }


@register.inclusion_tag('layouts/slider_block_home_page.html')
def slider_block():
    """
    Слайдер
    :return: title, description, slideimg, namebutton, linkbutton
    """
    sliders = Slider.objects.filter(available=True)
    return {'sliders': sliders, }


@register.inclusion_tag('layouts/news_block_home_page.html')
def news_block():
    news = News.objects.all()[:1]
    return {'news': news, }
