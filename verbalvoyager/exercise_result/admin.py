from django.contrib import admin

from logging_app.helpers import log_action

from .filters import StudentsListFilter, TeachersListFilter
from .models import (
    ExerciseDialogResult,
    ExerciseIrregularEnglishVerbResult,
    ExerciseWordsResult,
)


class AbstractExerciseResultAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


@admin.register(ExerciseWordsResult)
class ExerciseWordsResultAdmin(AbstractExerciseResultAdmin):
    list_display = (
        'get_ex_name', 'get_teacher', 'get_student',
        'step_1', 'step_2', 'step_3', 'step_4', 'step_5'
    )


@admin.register(ExerciseDialogResult)
class ExerciseDialogResultAdmin(AbstractExerciseResultAdmin):
    list_display = ('get_ex_name', 'get_teacher', 'get_student', 'points')


@admin.register(ExerciseIrregularEnglishVerbResult)
class ExerciseIrregularEnglishVerbResultAdmin(AbstractExerciseResultAdmin):
    list_display = (
        'get_ex_name', 'get_teacher', 'get_student',
        'step_1', 'step_2', 'step_3'
    )
