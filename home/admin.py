from django.contrib import admin
from home.models import Header, SeoHomePage


@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'phone_one', 'phone_two', )


@admin.register(SeoHomePage)
class SeoHomePage(admin.ModelAdmin):
    list_display = ('name_element', 'title_home_page', )
