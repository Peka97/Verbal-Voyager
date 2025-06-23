from django.contrib import admin

# from .models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult, ExerciseRussianWordsResult, ExerciseSpanishWordsResult, ExerciseEnglishDialogResult, ExerciseFrenchDialogResult, ExerciseSpanishDialogResult, ExerciseRussianDialogResult, ExerciseIrregularEnglishVerbResult
from .models import ExerciseWordsResult, ExerciseDialogResult, NewExerciseIrregularEnglishVerbResult
from .filters import TeachersListFilter, StudentsListFilter
from logging_app.helpers import log_action


# class AbstractExerciseWordsResultAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('get_ex_name', 'get_teacher', 'get_student',
#                     'step_1', 'step_2', 'step_3', 'step_4', 'step_5')
#     list_filter = [
#         TeachersListFilter,
#         StudentsListFilter,
#     ]

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


# @admin.register(ExerciseEnglishWordsResult)
# class ExerciseEnglishWordsResultAdmin(AbstractExerciseWordsResultAdmin):
#     pass


# @admin.register(ExerciseFrenchWordsResult)
# class ExerciseFrenchWordsResultAdmin(AbstractExerciseWordsResultAdmin):
#     pass


# @admin.register(ExerciseRussianWordsResult)
# class ExerciseRussianWordsResultAdmin(AbstractExerciseWordsResultAdmin):
#     pass


# @admin.register(ExerciseSpanishWordsResult)
# class ExerciseSpanishWordsResultAdmin(AbstractExerciseWordsResultAdmin):
#     pass


# class AbstractExerciseDialogResultAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('get_ex_name', 'get_teacher', 'get_student',
#                     'points')
#     list_filter = [
#         TeachersListFilter,
#         StudentsListFilter,
#     ]

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


# @admin.register(ExerciseEnglishDialogResult)
# class ExerciseEnglishDialogResultAdmin(AbstractExerciseDialogResultAdmin):
#     pass


# @admin.register(ExerciseFrenchDialogResult)
# class ExerciseFrenchDialogResultAdmin(AbstractExerciseDialogResultAdmin):
#     pass


# @admin.register(ExerciseSpanishDialogResult)
# class ExerciseSpanishDialogResultAdmin(AbstractExerciseDialogResultAdmin):
#     pass


# @admin.register(ExerciseRussianDialogResult)
# class ExerciseRussianDialogResultAdmin(AbstractExerciseDialogResultAdmin):
#     pass


# @admin.register(ExerciseIrregularEnglishVerbResult)
# class ExerciseIrregularEnglishVerbResultAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('get_ex_name', 'get_teacher', 'get_student',
#                     'step_1', 'step_2', 'step_3')
#     list_filter = [
#         TeachersListFilter,
#         StudentsListFilter,
#     ]

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('exercise', 'exercise__teacher', 'exercise__student')


# New models

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


@admin.register(NewExerciseIrregularEnglishVerbResult)
class NewExerciseIrregularEnglishVerbResultAdmin(AbstractExerciseResultAdmin):
    list_display = (
        'get_ex_name', 'get_teacher', 'get_student',
        'step_1', 'step_2', 'step_3'
    )
