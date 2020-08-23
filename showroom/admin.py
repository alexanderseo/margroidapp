from django.contrib import admin
from showroom.models import ShowRoomModel, Fotogalery


class FotogaleryInline(admin.StackedInline):
    model = Fotogalery


@admin.register(ShowRoomModel)
class ShowRoomModelAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'name', )
    inlines = [FotogaleryInline]
