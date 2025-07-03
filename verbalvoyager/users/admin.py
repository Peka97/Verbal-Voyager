from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from pages.filters import DropdownFilter, RelatedDropdownFilter

from .models import User


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
    readonly_fields = [
        'last_login', 'date_joined',
        # 'username', 'password'
    ]
    fieldsets = (
        ('User Info', {'fields': ('first_name',
         'last_name', 'email', 'timezone')}),
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

    # @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.username != 'admin':
            queryset = queryset \
            .exclude(username='admin') \
            .exclude(groups__name__in=['TeacherDemo'])

        return queryset.prefetch_related('groups')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        user = request.user

        if user.username != 'admin' and request.user.groups.filter(name='Teacher').exists():
            new_fieldsets = list(fieldsets)
            new_fieldsets = [
                fs for fs in new_fieldsets if fs[0] != 'User Advanced Permissions']

            return tuple(new_fieldsets)
        return fieldsets

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'groups':
            user = request.user

            if user.username != 'admin' and user.groups.filter(name='Teacher').exists():
                kwargs['queryset'] = Group.objects.filter(name__in=['Student', 'StudentDemo'])
        return super().formfield_for_manytomany(db_field, request, **kwargs)
