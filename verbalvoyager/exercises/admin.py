from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from logger import get_logger

from pages.filters import DropdownFilter, RelatedDropdownFilter
from .filters import TeachersListFilter, StudentsListFilter

from .models import ExerciseCategory, ExerciseEnglishWords, ExerciseFrenchWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb
from .forms import ExerciseDialogAdminForm, ExerciseIrregularEnglishVerbAdminForm


logger = get_logger()

User = get_user_model()

# Category


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    search_fields = ['pk', 'name']
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']


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

    fieldsets = (
        ('ExerciseWord Main', {
            'fields': (('name', 'category', 'student'), 'words',),
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
        TeachersListFilter,
        StudentsListFilter,
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]
    fieldsets = (
        ('ExerciseDialog Main', {
            'fields': (('name', 'category', 'student'), 'words', 'text'),
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
        TeachersListFilter,
        StudentsListFilter,
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]
    fieldsets = (
        ('ExerciseIrregularVerb Main', {
            'fields': (('name', 'category', 'student'), 'words', ),
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
