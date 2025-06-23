from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q, Case, When, Value, IntegerField, JSONField
from django_json_widget.widgets import JSONEditorWidget

from .models import Language, Word, Translation, EnglishWordDetail, FrenchWordDetail, SpanishWordDetail
from .models import NewEnglishVerb, NewFrenchVerb
from pages.filters import ChoiceDropdownFilter
from logging_app.helpers import log_action
from .filters import WordLanguageFilter, InvalidWordsFilter
from .services.normalizers import normalize_words
from .forms import TranslationAdminForm


# @admin.register(EnglishWord)
# class WordAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('word', 'speech_code', 'translation')
#     search_fields = ('word', 'translation')
#     readonly_fields = ('another_means', )
#     fieldsets = (
#         ('EnglishWord Main', {
#             'fields': (('word', 'translation',), 'another_means', ('prefix', 'speech_code')),
#         }),
#         ('EnglishWord Extra', {
#             'classes': ('collapse', ),
#             'fields': ('transcription', 'definition', 'examples', ),
#         }),
#         ('EnglishWord Media', {
#             'classes': ('collapse', ),
#             'fields': ('image_url', 'sound_url'),
#         })
#     )
#     save_as = True

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)

#     class Media:
#         js = ['admin/js/load_data_from_api_UI.js',]


# @admin.register(FrenchWord)
# class FrenchWordAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('word', 'genus', 'translation')
#     list_filter = (('genus', ChoiceDropdownFilter),)
#     readonly_fields = ('another_means', )
#     search_fields = ('word', 'translation')
#     fieldsets = (
#         ('FrenchWord Main', {
#             'fields': (('word', 'translation'), 'another_means', ('genus')),
#         }),
#         ('FrenchWord Extra', {
#             'classes': ('collapse', ),
#             'fields': ('examples', ),
#         }),
#         ('FrenchWord Media', {
#             'classes': ('collapse', ),
#             'fields': ('image_url', 'sound_url'),
#         })
#     )
#     save_as = True

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)


# @admin.register(FrenchVerb)
# class FrenchVerbAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     autocomplete_fields = ('infinitive', )
#     list_display = ('infinitive', 'participe_present', 'participe_passe')
#     search_fields = ('infinitive__word',
#                      'participe_present', 'participe_passe')
#     fieldsets = (
#         ('FrenchVerb Main', {
#             'fields': ('infinitive', 'participe_present', 'participe_passe',),
#         }),
#         ('FrenchVerb Indicatif présent', {
#             'classes': ('collapse', ),
#             'fields': (
#                 'indicatif_j',
#                 'indicatif_tu',
#                 'indicatif_il',
#                 'indicatif_nous',
#                 'indicatif_vous',
#                 'indicatif_ils',

#             ),
#         })
#     )

#     save_as = True

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)


# @admin.register(IrregularEnglishVerb)
# class IrregularEnglishVerbAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     autocomplete_fields = ('infinitive', )
#     list_display = ('infinitive', 'past_simple', 'past_participle')
#     search_fields = ('infinitive__word', 'past_simple', 'past_participle')
#     save_as = True

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)


# @admin.register(SpanishWord)
# class SpanishWordAdmin(admin.ModelAdmin):
#     show_full_result_count = False
#     list_display = ('word', 'translation')
#     search_fields = ('word', 'translation')
#     readonly_fields = ('another_means', )
#     fieldsets = (
#         ('SpanishWord Main', {
#             'fields': (('word', 'translation',), 'another_means', ('prefix', )),
#         }),
#         ('SpanishWord Extra', {
#             'classes': ('collapse', ),
#             'fields': ('transcription', 'definition', 'examples', ),
#         }),
#         ('SpanishWord Media', {
#             'classes': ('collapse', ),
#             'fields': ('image_url', 'sound_url'),
#         })
#     )
#     save_as = True

#     @log_action
#     def save_model(self, request, obj, form, change):
#         return super().save_model(request, obj, form, change)


class BaseAdmin(admin.ModelAdmin):
    show_full_result_count = False


# class WordDetailInline(admin.TabularInline):
#     model =
#     extra = 0
#     min_num = 1
#     max_num = 1

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('word')


@admin.register(Language)
class LanguageAdmin(BaseAdmin):
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(Word)
class WordAdmin(BaseAdmin):
    list_display = ('word', 'language', 'created_at', 'updated_at')
    search_fields = ('word', )
    list_select_related = ('language',)
    list_filter = (
        ('language', admin.RelatedOnlyFieldListFilter),
        InvalidWordsFilter,
    )
    ordering = ('word',)
    actions = ['normalize_words_action',]
    # inlines = [SourceWordDetailInline,]

    def has_details(self, obj):
        return obj.details is not None
    has_details.boolean = True
    has_details.short_description = _('Has details')

    # TODO: copy from Translation method
    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return queryset, False

        queryset = queryset.filter(word__icontains=search_term)

        vector = SearchVector('word')
        query = SearchQuery(search_term)
        queryset = queryset.annotate(
            rank=SearchRank(vector, query),
            exact_match=Case(
                When(word__iexact=search_term, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-exact_match', '-rank', 'word')

        return queryset, False

    def normalize_words_action(self, request, queryset):
        try:
            normalize_words(queryset)

            message = "Слова успешно нормализованы!"
            level = messages.SUCCESS

            self.message_user(request, message, level, extra_tags='safe')

        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:

            if 'normalize_words_action' in actions:
                del actions['normalize_words_action']
        return actions

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(Translation)
class TranslationAdmin(BaseAdmin):
    form = TranslationAdminForm
    save_as = True
    search_fields = ('source_word__word', 'target_word__word')
    autocomplete_fields = ('source_word', 'target_word')
    list_display = ('source_word__word', 'target_word__word', )
    search_fields = ('source_word__word', 'target_word__word')
    list_filter = (WordLanguageFilter,)
    ordering = ('source_word__word', 'target_word__word')
    fieldsets = (
        ('Translation Main', {
            'fields': (('source_word', 'target_word'),),
        }),
        ('Translation Extra', {
            'classes': ('collapse', ),
            'fields': ('part_of_speech', 'definition', 'examples', 'prefix'),
        }),
    )
    # formfield_overrides = {
    #     JSONField: {'widget': JSONEditorWidget},
    # }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('source_word', 'target_word')

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return queryset, False

        queryset = queryset.filter(
            Q(source_word__word__icontains=search_term) |
            Q(target_word__word__icontains=search_term)
        )

        vector = SearchVector('source_word', 'target_word')
        query = SearchQuery(search_term)
        queryset = queryset.annotate(
            rank=SearchRank(vector, query),
            exact_match=Case(
                When(source_word__word__iexact=search_term, then=Value(3)),
                When(source_word__word__iexact=search_term, then=Value(3)),
                When(source_word__word__istartswith=search_term, then=Value(2)),
                When(source_word__word__istartswith=search_term, then=Value(2)),
                When(source_word__word__icontains=search_term, then=Value(1)),
                When(source_word__word__icontains=search_term, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-exact_match', '-rank', 'source_word', 'target_word')

        return queryset, False

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    class Media:
        js = ['admin/js/load_translation_data.js',]


class AbstractWordDetailAdmin(BaseAdmin):
    list_display = ('word',)
    search_fields = ('word__word', )
    autocomplete_fields = ('word', )

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(EnglishWordDetail)
class EnglishWordDetailAdmin(AbstractWordDetailAdmin):
    pass


@admin.register(FrenchWordDetail)
class FrenchWordDetailAdmin(AbstractWordDetailAdmin):
    pass


@admin.register(SpanishWordDetail)
class SpanishWordDetailAdmin(AbstractWordDetailAdmin):
    pass


# @admin.register(RussianWordDetail)
# class RussianWordDetailAdmin(AbstractWordDetailAdmin):
#     pass


@admin.register(NewEnglishVerb)
class NewEnglishVerbAdmin(admin.ModelAdmin):
    show_full_result_count = False
    autocomplete_fields = ('infinitive', )
    list_display = ('infinitive__word', 'past_simple', 'past_participle')
    search_fields = ('infinitive__word', 'past_simple', 'past_participle')
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('infinitive')


@admin.register(NewFrenchVerb)
class NewFrenchVerbAdmin(admin.ModelAdmin):
    show_full_result_count = False
    autocomplete_fields = ('infinitive', )
    list_display = ('infinitive__word', 'participe_present', 'participe_passe')
    search_fields = ('infinitive__word',
                     'participe_present', 'participe_passe')
    fieldsets = (
        ('FrenchVerb Main', {
            'fields': ('infinitive', 'participe_present', 'participe_passe',),
        }),
        ('FrenchVerb Indicatif présent', {
            'classes': ('collapse', ),
            'fields': (
                'indicatif_j',
                'indicatif_tu',
                'indicatif_il',
                'indicatif_nous',
                'indicatif_vous',
                'indicatif_ils',

            ),
        })
    )

    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('infinitive')
