from django.contrib import admin
from home.models import Header, SeoHomePage, ContactBlockHomePage, ContactBlockFooter, Slider


@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'phone_one', 'phone_two', )


@admin.register(SeoHomePage)
class SeoHomePageAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'title_home_page', )


@admin.register(ContactBlockHomePage)
class ContactBlockHomePageAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'phone_one', 'text_header', )


@admin.register(ContactBlockFooter)
class ContactBlockFooterAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'email', 'phone_one', 'phone_two', )


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('name', 'available', )
