from django.contrib import admin
from nested_admin import NestedStackedInline, NestedModelAdmin

from .models import EnglishLessonPlan, EnglishLessonMainAims, EnglishLessonSubsidiaryAims

# Register your models here.


class EnglishLessonMainAimsInline(NestedStackedInline):
    model = EnglishLessonMainAims
    extra = 0
    fk_name = 'lesson_plan_id'


class EnglishLessonSubsidiaryAimsInline(NestedStackedInline):
    model = EnglishLessonSubsidiaryAims
    extra = 0
    fk_name = 'lesson_plan_id'


@admin.register(EnglishLessonPlan)
class EnglishLessonPlanAdmin(NestedModelAdmin):
    show_full_result_count = False
    list_display = ('pk', 'lesson_id', 'theme')
    autocomplete_fields = ('new_vocabulary', 'exercise_id')
    inlines = [
        EnglishLessonMainAimsInline,
        EnglishLessonSubsidiaryAimsInline,
    ]

    fieldsets = (
        ('Lesson Plan Info', {
            'fields': (('theme', 'lesson_id'), ),
        }),
        ('Vocabulary Info', {
            'fields': (('new_vocabulary', 'exercise_id'),)
        }),
        ('Additional Info', {
            'fields': ('processes', 'materials',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('new_vocabulary').select_related('lesson_id')


@admin.register(EnglishLessonMainAims)
class EnglishLessonMainAimsAdmin(admin.ModelAdmin):
    show_full_result_count = False


@admin.register(EnglishLessonSubsidiaryAims)
class EnglishLessonSubsidiaryAimsAdmin(admin.ModelAdmin):
    show_full_result_count = False
