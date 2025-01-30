import logging

from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import path
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import EnglishWord, FrenchWord, ExerciseWords, ExerciseEnglishWords, ExerciseFrenchWords, ExerciseDialog, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseWordsResult, ExerciseDialogResult
from .forms import ExerciseWordsAdminForm, ExerciseDialogAdminForm


logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.addHandler(logging.FileHandler(DEBUG_LOGGING_FP))

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
        teachers = User.objects.filter(groups__name='Teacher')

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
                ExerciseWordsResult,                
                ExerciseDialogResult
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
        students = User.objects.filter(groups__name='Student')

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
            if len(queryset) >= 1 and isinstance(queryset[0], (ExerciseWordsResult, ExerciseDialogResult)):
                return queryset.filter(
                    exercise__student=self.value()
                )
            else:
                return queryset.filter(
                    student=self.value()
                )

@admin.register(ExerciseWords)
class ExerciseWordsAdmin(admin.ModelAdmin):
    filter_horizontal = ('words', )
    search_fields = ('pk', 'teacher__username')
    autocomplete_fields = ('student', )
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

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
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
        form = super(ExerciseWordsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['student'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form

@admin.register(ExerciseEnglishWords)
class ExerciseEnglishWordsAdmin(admin.ModelAdmin):
    filter_horizontal = ('words', )
    search_fields = ('pk', 'teacher__username')
    autocomplete_fields = ('student', )
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
            'fields': (('name','student'), 'words',),
        }),
        ('ExerciseWord Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access'),
        })
    )

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
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
        form = super(ExerciseEnglishWordsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['student'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form


@admin.register(ExerciseFrenchWords)
class ExerciseFrenchWordsAdmin(admin.ModelAdmin):
    filter_horizontal = ('words', )
    search_fields = ('pk', 'teacher__username')
    autocomplete_fields = ('student', )
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
            'fields': (('name','student'), 'words',),
        }),
        ('ExerciseWord Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access'),
        })
    )

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
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
        form = super(ExerciseFrenchWordsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['student'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form


@admin.register(EnglishWord)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translate')
    # list_filter = ['lang', ]
    search_fields = ('word', 'translate')
    fieldsets = (
        ('EnglishWord Main', {
            'fields': (('word', 'translate'), ),
        }),
        ('EnglishWord Extra', {
            'classes': ('collapse', ),
            'fields': ('sentences', ),
        })
    )
    

@admin.register(FrenchWord)
class FrenchWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'genus', 'translate')
    list_filter = ['genus', ]
    search_fields = ('word', 'translate')
    fieldsets = (
        ('EnglishWord Main', {
            'fields': (('word', 'genus'), 'translate'),
        }),
        ('EnglishWord Extra', {
            'classes': ('collapse', ),
            'fields': ('sentences', ),
        })
    )


@admin.register(ExerciseWordsResult)
class ExerciseEnglishWordsResultAdmin(admin.ModelAdmin):
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'step_1', 'step_2', 'step_3', 'step_4')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('words', 'words__teacher', 'words__student')


@admin.register(ExerciseDialogResult)
class ExerciseDialogResultAdmin(admin.ModelAdmin):
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'points')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('dialog', 'dialog__teacher', 'dialog__student')


@admin.register(ExerciseDialog)
class ExerciseDialogAdmin(admin.ModelAdmin):
    form = ExerciseDialogAdminForm
    search_fields = ['student', ]
    autocomplete_fields = ('student', )
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

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExerciseDialogAdmin, self).get_form(
            request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher', ])

        return form

    def clean(self):
        cleaned_data = super(ExerciseDialogAdminForm, self).clean()
        field_value = cleaned_data.get('field_name')
        if not field_value:
            raise ValidationError('No value for field_name')

    class Media:
        js = ['admin/js/generate_dialog_text.js',]
        css = {
            'all': ('admin/css/dialog.css', )
        }


# @admin.register(ExerciseDialog)
class AbstractExerciseDialogAdmin(admin.ModelAdmin):
    form = ExerciseDialogAdminForm
    search_fields = ['student', ]
    autocomplete_fields = ('student', )
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

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExerciseDialogAdmin, self).get_form(
            request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher', ])

        return form

    def clean(self):
        cleaned_data = super(ExerciseDialogAdminForm, self).clean()
        field_value = cleaned_data.get('field_name')
        if not field_value:
            raise ValidationError('No value for field_name')

    class Media:
        js = ['admin/js/generate_dialog_text.js',]
        css = {
            'all': ('admin/css/dialog.css', )
        }

@admin.register(ExerciseEnglishDialog)
class ExerciseEnglishDialogAdmin(AbstractExerciseDialogAdmin):
    pass

@admin.register(ExerciseFrenchDialog)
class ExerciseFrenchDialogAdmin(AbstractExerciseDialogAdmin):
    pass
