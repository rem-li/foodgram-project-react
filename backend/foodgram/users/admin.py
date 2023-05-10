from django.conf import settings
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки раздела пользователей."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role'
    )
    empty_value_display = 'значение отсутствует'
    list_editable = ('role',)
    list_filter = ('username', 'role')
    # list_per_page = settings.LIST_PER_PAGE
    search_fields = ('username', 'role')
