from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from advertisements.models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "breed", "status", "created_at", "get_photo", "actions_column"]
    list_filter = ["status", "breed", "created_at", "type", "color", "sex"]
    search_fields = ["title", "description", "author", "breed", "location"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 20
    actions = ["mark_as_found", "mark_as_lost", "delete_selected", "delete_all_advertisements"]
    ordering = ["-created_at"]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author', 'phone', 'photo')
        }),
        ('Характеристики животного', {
            'fields': ('type', 'breed', 'color', 'sex', 'eye_color', 'face_shape', 'special_features')
        }),
        ('Местоположение', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Статус и даты', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
        ('Дополнительно', {
            'fields': ('social_media',)
        }),
    )

    def get_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.photo.url)
        return "Нет фото"
    get_photo.short_description = "Фото"

    def actions_column(self, obj):
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a class="button" href="{}delete/" style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">Удалить</a>'
            '</div>',
            f"/admin/advertisements/advertisement/{obj.id}/"
        )
    actions_column.short_description = "Действия"
    actions_column.allow_tags = True

    def mark_as_found(self, request, queryset):
        queryset.update(status="found")
    mark_as_found.short_description = "Отметить как найденных"

    def mark_as_lost(self, request, queryset):
        queryset.update(status="lost")
    mark_as_lost.short_description = "Отметить как потерянных"

    def delete_all_advertisements(self, request, queryset):
        # Получаем общее количество объявлений
        total = Advertisement.objects.count()
        # Удаляем все объявления
        Advertisement.objects.all().delete()
        # Показываем сообщение об успешном удалении
        messages.success(request, f'Успешно удалено {total} объявлений')
    delete_all_advertisements.short_description = "Удалить все объявления"

    def has_delete_permission(self, request, obj=None):
        return True  # Разрешаем удаление всем пользователям с доступом к админ-панели

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
