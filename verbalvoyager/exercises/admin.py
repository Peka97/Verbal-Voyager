import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .filters import TeachersListFilter, StudentsListFilter
from .models import ExerciseCategory, ExerciseEnglishWords, ExerciseFrenchWords, \
    ExerciseRussianWords, ExerciseSpanishWords, ExerciseEnglishDialog, \
    ExerciseFrenchDialog, ExerciseRussianDialog, ExerciseSpanishDialog, \
    ExerciseIrregularEnglishVerb
from .forms import ExerciseDialogAdminForm, ExerciseIrregularEnglishVerbAdminForm
from pages.filters import DropdownFilter, RelatedDropdownFilter
from logging_app.helpers import log_action


logger = logging.getLogger('django')

User = get_user_model()

# Category


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    search_fields = ['pk', 'name']
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


# ExerciseWords
class AbstractExerciseWordsAdmin(admin.ModelAdmin):
    show_full_result_count = False
    filter_horizontal = ('words', )
    search_fields = ['pk', 'student__pk', 'student__first_name',
                     'student__last_name', 'name', 'category__pk', 'category__name']
    autocomplete_fields = ('student', 'words', 'category')
    list_display = (
        'pk', 'name', 'is_active', 'student', 'teacher', 'get_words', 'external_access', 'source_link',
    )
    list_display_links = ('name', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]
    save_as = True
    actions = ['make_active', 'make_inactive']
    readonly_fields = ['created_at', ]

    fieldsets = (
        ('ExerciseWord Main', {
            'fields': (('name', 'category', 'student'), 'words',),
        }),
        ('ExerciseWord Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access', 'created_at',),
        })
    )

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_absolute_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.username != 'admin':
            queryset = queryset \
                .exclude(student__groups__name='StudentDemo') \
                .exclude(teacher__groups__name='TeacherDemo')

        return queryset.select_related('student', 'teacher').prefetch_related('words')

    @admin.action(description='Активировать')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивировать')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.username != 'admin':
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


@admin.register(ExerciseRussianWords)
class ExerciseRussianWordsAdmin(AbstractExerciseWordsAdmin):
    pass


@admin.register(ExerciseSpanishWords)
class ExerciseSpanishWordsAdmin(AbstractExerciseWordsAdmin):
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
        TeachersListFilter,
        StudentsListFilter,
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]
    readonly_fields = ['created_at', ]
    fieldsets = (
        ('ExerciseDialog Main', {
            'fields': (('name', 'category', 'student'), 'words', 'text'),
        }),
        ('ExerciseDialog Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access', 'created_at'),
        })
    )
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.username != 'admin':
            queryset = queryset \
                .exclude(student__groups__name='StudentDemo') \
                .exclude(teacher__groups__name='TeacherDemo')

        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_autocomplete_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.user.username != 'admin':
            group_name = 'Student'
            print(queryset)
            queryset = queryset.filter(student__groups__name=group_name)

        return queryset, use_distinct

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.username != 'admin':
            form.base_fields['teacher'].initial = request.user
            form.base_fields['teacher'].queryset = User.objects.filter(
                groups__name__in=['Teacher'])
            form.base_fields['student'].queryset = User.objects.filter(
                groups__name__in=['Student'])

        return form

    def clean(self):
        super(ExerciseDialogAdminForm, self).clean()

    class Media:
        css = {
            'all': (
                'admin/css/dialog.css',
                'fontawesomefree/css/fontawesome.css',
                'fontawesomefree/css/brands.css',
                'fontawesomefree/css/solid.css'
            )
        }
        js = [
            'admin/js/generate_dialog_ui_load_and_fetch.js',
        ]


@admin.register(ExerciseEnglishDialog)
class ExerciseEnglishDialogAdmin(AbstractExerciseDialogAdmin):
    pass


@admin.register(ExerciseFrenchDialog)
class ExerciseFrenchDialogAdmin(AbstractExerciseDialogAdmin):
    pass


@admin.register(ExerciseRussianDialog)
class ExerciseRussianDialogAdmin(AbstractExerciseDialogAdmin):
    pass


@admin.register(ExerciseSpanishDialog)
class ExerciseSpanishDialogAdmin(AbstractExerciseDialogAdmin):
    pass


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
        TeachersListFilter,
        StudentsListFilter,
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]
    readonly_fields = ['created_at', ]
    fieldsets = (
        ('ExerciseIrregularVerb Main', {
            'fields': (('name', 'category', 'student'), 'words', ),
        }),
        ('ExerciseDialog Options', {
            'classes': ('collapse', ),
            'fields': ('teacher', 'is_active', 'external_access', 'created_at'),
        })
    )
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.username != 'admin':
            queryset = queryset \
                .exclude(student__groups__name='StudentDemo') \
                .exclude(teacher__groups__name='TeacherDemo')

        return queryset.select_related('student', 'teacher').prefetch_related('words')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.username != 'admin':
            form.base_fields['teacher'].initial = request.user
            form.base_fields['teacher'].queryset = User.objects.filter(
                groups__name__in=['Teacher'])
            form.base_fields['student'].queryset = User.objects.filter(
                groups__name__in=['Student'])

        return form

    def clean(self):
        cleaned_data = super(ExerciseIrregularEnglishVerb, self).clean()
        field_value = cleaned_data.get('field_name')
        if not field_value:
            raise ValidationError('No value for field_name')
