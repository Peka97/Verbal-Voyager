from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from pages.filters import DropdownFilter, RelatedDropdownFilter


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    show_full_result_count = False
    list_display = (
        'username', 'last_name', 'first_name', 'get_groups', 'email',
    )
    list_filter = (
        ('groups', RelatedDropdownFilter),
        ('is_staff', DropdownFilter),
        ('is_superuser', DropdownFilter),
    )
    fieldsets = (
        ('User Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('User Permissions', {'fields': ('groups', )}),
        ('User Credentials',
            {
                'classes': ('collapse',),
                'fields': ('username', 'password',)
            }
         ),
        ('User Advanced Permissions', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'user_permissions')
        }
        ),
        ('User Dates',
            {
                'classes': ('collapse',),
                'fields': ('last_login', 'date_joined')
            }
         ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('groups')
