from django.contrib import admin

from .models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult, ExerciseEnglishDialogResult, ExerciseFrenchDialogResult, ExerciseIrregularEnglishVerbResult
from .filters import TeachersListFilter, StudentsListFilter


class AbstractExerciseWordsResultAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'step_1', 'step_2', 'step_3', 'step_4')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


@admin.register(ExerciseEnglishWordsResult)
class ExerciseEnglishWordsResultAdmin(AbstractExerciseWordsResultAdmin):
    pass


@admin.register(ExerciseFrenchWordsResult)
class ExerciseFrenchWordsResultAdmin(AbstractExerciseWordsResultAdmin):
    pass


class AbstractExerciseDialogResultAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'points')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


@admin.register(ExerciseEnglishDialogResult)
class ExerciseEnglishDialogResultAdmin(AbstractExerciseDialogResultAdmin):
    pass


@admin.register(ExerciseFrenchDialogResult)
class ExerciseFrenchDialogResultAdmin(AbstractExerciseDialogResultAdmin):
    pass


@admin.register(ExerciseIrregularEnglishVerbResult)
class ExerciseIrregularEnglishVerbResultAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'step_1', 'step_2', 'step_3')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')
