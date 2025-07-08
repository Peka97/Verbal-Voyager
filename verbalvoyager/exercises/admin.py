import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.db.models import Prefetch

from dictionary.models import Translation, Word, Language

from .filters import TeachersListFilter, StudentsListFilter
from .models import ExerciseCategory, ExerciseWords, \
    ExerciseIrregularEnglishVerb, ExerciseDialog
from .forms import NewExerciseDialogAdminForm, NewWordsExerciseForm
from pages.filters import DropdownFilter, RelatedDropdownFilter
from logging_app.helpers import log_action


logger = logging.getLogger('django')

User = get_user_model()


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    search_fields = ['pk', 'name']
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(ExerciseWords)
class ExerciseWordsAdmin(admin.ModelAdmin):
    form = NewWordsExerciseForm
    show_full_result_count = False
    save_as = True
    search_fields = [
        'pk', 'student__pk', 'student__first_name', 'student__last_name',
        'name', 'words__source_word__word', 'words__target_word__word',
    ]
    autocomplete_fields = ('words', 'student', 'teacher')
    filter_horizontal = ('words', )
    list_display = (
        'pk', 'name', 'is_active', 'student', 'teacher',
        'get_words', 'external_access', 'source_link'
    )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        # ('lang', RelatedDropdownFilter),
        ('category', RelatedDropdownFilter),
        ('is_active', DropdownFilter),
        ('external_access', DropdownFilter),
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Метод вызывает ошибки

        # if request.user.username != 'admin':
        #     queryset = queryset \
        #         .exclude(student__groups__name='StudentDemo') \
        #         .exclude(teacher__groups__name='TeacherDemo')

        language_prefetched = Prefetch(
            'language', queryset=Language.objects.all())
        words_prefetched = (
            Prefetch('source_word', queryset=Word.objects.prefetch_related(
                language_prefetched).all()),
            Prefetch('target_word', queryset=Word.objects.prefetch_related(
                language_prefetched).all()),
        )
        exercise_prefetched = (
            Prefetch(
                'words', queryset=Translation.objects.prefetch_related(*words_prefetched).all()),
            # Prefetch(
            #     'lang', queryset=Language.objects.all())
        )

        return queryset.select_related('student', 'teacher').prefetch_related(*exercise_prefetched)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.username != 'admin':
            form.base_fields['teacher'].initial = request.user
            form.base_fields['teacher'].queryset = User.objects.filter(
                groups__name__in=['Teacher'])
            form.base_fields['student'].queryset = User.objects.filter(
                groups__name__in=['Student'])

        return form

    def source_link(self, obj):
        return mark_safe(f'<a href={obj.get_url()}>Перейти<a>')
    source_link.short_description = 'Ссылка на упражнение'

    # def clean(self):
    #     super().clean()
    #     print('CLEAN')

    #     if self.pk:
    #         for translation in self.words.all():
    #             print(self.lang.name)
    #             print(translation.source_word.language)
    #             if self.lang.name == 'Russian' and translation.source_word.language.name != 'English':
    #                 raise ValidationError(
    #                     f'Слово "{translation}" не подходит для языка "{self.lang.name}". Для русского языка нужно использовать английские слова.')
    #             elif translation.source_word.language != self.lang:
    #                 raise ValidationError(
    #                     f'Слово "{translation}" не подходит для языка "{self.lang.name}"')


@admin.register(ExerciseIrregularEnglishVerb)
class ExerciseIrregularEnglishVerbAdmin(admin.ModelAdmin):
    show_full_result_count = False
    save_as = True
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


@admin.register(ExerciseDialog)
class ExerciseDialogAdmin(admin.ModelAdmin):
    show_full_result_count = False
    form = NewExerciseDialogAdminForm
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
            'fields': (('name', 'category', 'student'), 'lang', 'words', 'text'),
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
        super().clean()

        if self.pk:
            for translation in self.words.all():
                if translation.source_word.language != self.lang:
                    raise ValidationError(
                        f'Слово "{translation}" не подходит для языка "{self.lang.name}"')

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
            'admin/js/generate_dialog.js',
        ]
