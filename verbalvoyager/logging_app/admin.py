from django.contrib import admin
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder

from .filters import TeachersListFilter
from .models import ActionLog


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'content_object')
    list_filter = (
        TeachersListFilter,
        ('timestamp',
         DateRangeQuickSelectListFilterBuilder(title='Дата записи')
         ),
    )
    readonly_fields = ('timestamp', 'user', 'content_type',
                       'object_id', 'content_object', 'action', 'description')
