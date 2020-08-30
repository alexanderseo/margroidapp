from django.contrib import admin
from news.models import News, PageNewsSeo


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PageNewsSeo)
class PageNewsSeoAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'description',)
