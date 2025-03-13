import logging

from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from logger import get_logger
from .models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb
from exercise_result.models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult, ExerciseEnglishDialogResult, ExerciseFrenchDialogResult, ExerciseIrregularEnglishVerbResult
from .forms import ExerciseDialogAdminForm, ExerciseIrregularEnglishVerbAdminForm


logger = get_logger()

User = get_user_model()


# Filters
class TeachersListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Учитель")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "teacher"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        teachers = User.objects.filter(
            groups__name='Teacher').order_by('last_name', 'first_name')

        return [
            (teacher.pk, _(f'{teacher.last_name} {teacher.first_name}')) for teacher in teachers
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            if len(queryset) >= 1 and isinstance(queryset[0], (
                ExerciseEnglishWordsResult,
                ExerciseFrenchWordsResult,
                ExerciseEnglishDialogResult,
                ExerciseFrenchDialogResult,
                ExerciseIrregularEnglishVerbResult
            )):
                return queryset.filter(
                    exercise__teacher=self.value()
                )
            else:
                return queryset.filter(
                    teacher=self.value()
                )


class StudentsListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Ученик")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "student"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        students = User.objects.filter(
            groups__name='Student').order_by('last_name', 'first_name')

        return [
            (student.pk, _(f'{student.last_name} {student.first_name}')) for student in students
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            if len(queryset) >= 1 and isinstance(queryset[0], (
                ExerciseEnglishWordsResult,
                ExerciseFrenchWordsResult,
                ExerciseEnglishDialogResult,
                ExerciseFrenchDialogResult,
                ExerciseIrregularEnglishVerbResult
            )):
                return queryset.filter(
                    exercise__student=self.value()
                )
            else:
                return queryset.filter(
                    student=self.value()
                )

# ExerciseWords


class AbstractExerciseWordsAdmin(admin.ModelAdmin):
    show_full_result_count = False
    filter_horizontal = ('words', )
    search_fields = ['pk', 'student__pk', 'student__first_name',
                     'student__last_name', 'name']
    autocomplete_fields = ('student', 'words')
    list_display = (
        'pk', 'name', 'is_active', 'student', 'teacher', 'get_words', 'external_access', 'source_link',
    )
    list_display_links = ('name', )
    list_filter = [
        'is_active',
        'external_access',
        TeachersListFilter,
        StudentsListFilter,
    ]
    save_as = True
    actions = ['make_active', 'make_inactive']

    fieldsets = (
        ('ExerciseWord Main', {
            'fields': (('name', 'student'), 'words',),
        }),
        ('ExerciseWord Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access'),
        })
    )

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.model.objects.filter(
                student=obj.student).exclude(pk=obj.pk).count()
            obj.name = f"Words {student_exercises_count + 1} "

        super().save_model(request, obj, form, change)

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_absolute_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'teacher').prefetch_related('words')

    @admin.action(description='Активировать')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивировать')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['student'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form


@admin.register(ExerciseEnglishWords)
class ExerciseEnglishWordsAdmin(AbstractExerciseWordsAdmin):
    pass


@admin.register(ExerciseFrenchWords)
class ExerciseFrenchWordsAdmin(AbstractExerciseWordsAdmin):
    pass


# ExerciseDialogs


class AbstractExerciseDialogAdmin(admin.ModelAdmin):
    show_full_result_count = False
    form = ExerciseDialogAdminForm
    search_fields = ['pk', 'student__pk', 'student__first_name',
                     'student__last_name', 'name']
    autocomplete_fields = ('words', 'student')
    filter_horizontal = ('words', )
    list_display = (
        'pk', 'name', 'is_active', 'student', 'teacher', 'get_words', 'external_access', 'source_link',
    )
    list_display_links = ('name', )
    list_filter = [
        'is_active',
        'external_access',
        TeachersListFilter,
        StudentsListFilter,
    ]
    fieldsets = (
        ('ExerciseDialog Main', {
            'fields': (('name', 'student'), 'words', 'text'),
        }),
        ('ExerciseDialog Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access'),
        })
    )
    save_as = True

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(
            request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher', ])

        return form

    def clean(self):
        super(ExerciseDialogAdminForm, self).clean()

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.model.objects.filter(
                student=obj.student).exclude(pk=obj.pk).count()
            obj.name = f"Dialog {student_exercises_count + 1} "

        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/dialog.css', )
        }


@admin.register(ExerciseEnglishDialog)
class ExerciseEnglishDialogAdmin(AbstractExerciseDialogAdmin):
    class Media:
        js = ['admin/js/generate_dialog_english_text.js',]


@admin.register(ExerciseFrenchDialog)
class ExerciseFrenchDialogAdmin(AbstractExerciseDialogAdmin):
    class Media:
        js = ['admin/js/generate_dialog_french_text.js',]


@admin.register(ExerciseIrregularEnglishVerb)
class ExerciseIrregularEnglishVerbAdmin(admin.ModelAdmin):
    show_full_result_count = False
    form = ExerciseIrregularEnglishVerbAdminForm
    search_fields = ['pk', 'student__pk', 'student__first_name',
                     'student__last_name', 'name']
    autocomplete_fields = ('words', 'student')
    filter_horizontal = ('words', )
    list_display = (
        'pk', 'name', 'is_active', 'student', 'teacher', 'get_words', 'external_access', 'source_link',
    )
    list_display_links = ('name', )
    list_filter = [
        'is_active',
        'external_access',
        TeachersListFilter,
        StudentsListFilter,
    ]
    fieldsets = (
        ('ExerciseIrregularVerb Main', {
            'fields': (('name', 'student'), 'words', ),
        }),
        ('ExerciseDialog Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access'),
        })
    )
    save_as = True

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(
            request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher', ])

        return form

    def clean(self):
        cleaned_data = super(ExerciseIrregularEnglishVerb, self).clean()
        field_value = cleaned_data.get('field_name')
        if not field_value:
            raise ValidationError('No value for field_name')

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.model.objects.filter(
                student=obj.student).exclude(pk=obj.pk).count()
            obj.name = f"Irregular Verbs {student_exercises_count + 1} "

        super().save_model(request, obj, form, change)
