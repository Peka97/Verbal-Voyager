from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'last_name', 'first_name', 'get_groups', 'email',
    )
    fieldsets = (
        ('Person Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('groups', )}),
        ('Credentials',
            {
                'classes': ('collapse',),
                'fields': ('username', 'password',)
            }
         ),
        ('Advanced Permissions', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'user_permissions')
            }
         ),
        ('Important dates', 
            {
                'classes': ('collapse',),
                'fields': ('last_login', 'date_joined')
            }
        ),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('groups')


