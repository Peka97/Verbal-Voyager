from django.contrib import admin
from django.utils.html import format_html

from .models import ExerciseType, Exercise, ExerciseConstructor, Document


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'template_name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description',
                    'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'words__word')
    ordering = ('-created_at',)
    autocomplete_fields = ('words',)


@admin.register(ExerciseConstructor)
class ExerciseConstructorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'config')
    search_fields = ('name',)
    ordering = ('pk',)


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
