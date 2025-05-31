from django.contrib import admin

from marks.models import Marks


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longtitude', 'breed', 'color', 'type', 'image')
    list_display_links = ('id', 'latitude', 'longtitude', 'breed', 'color', 'type', 'image')
    search_fields = ('id', 'latitude', 'longtitude', 'breed', 'color', 'type', 'image')
    list_filter = ('id', 'latitude', 'longtitude', 'breed', 'color', 'type', 'image')
    empty_value_display = '-пусто-'
