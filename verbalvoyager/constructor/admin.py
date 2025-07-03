from django.contrib import admin
from django.db.models import JSONField
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget

from .models import Document, LessonPage, LessonPageConstructor, ModuleType


@admin.register(ModuleType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'template_name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(LessonPage)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description',
                    'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'words__word')
    ordering = ('-created_at',)
    autocomplete_fields = ('words',)


@admin.register(LessonPageConstructor)
class ExerciseConstructorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'config')
    search_fields = ('name',)
    ordering = ('pk',)
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'file', 'original_name', 'display_name')
    search_fields = ('file',)
    ordering = ('-pk',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Скачать</a>', obj.file.url)
        return "-"
    file_link.short_description = "Файл"
