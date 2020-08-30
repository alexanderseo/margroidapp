from django.contrib import admin
from showroom.models import ShowRoomModel, FotogaleryShowRoom


class FotogaleryShowRoomInline(admin.StackedInline):
    model = FotogaleryShowRoom


@admin.register(ShowRoomModel)
class ShowRoomModelAdmin(admin.ModelAdmin):
    list_display = ('name_element', 'name', )
    inlines = [FotogaleryShowRoomInline]
