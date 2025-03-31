from django.contrib import admin
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder

from .models import ActionLog
from .filters import TeachersListFilter

# Register your models here.


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
