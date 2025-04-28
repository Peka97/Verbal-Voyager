from django.contrib import admin

from .models import EnglishWord, FrenchWord, IrregularEnglishVerb, SpanishWord
from pages.filters import ChoiceDropdownFilter
from logging_app.helpers import log_action


@admin.register(EnglishWord)
class WordAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('word', 'speech_code', 'translation')
    search_fields = ('word', 'translation')
    readonly_fields = ('another_means', )
    fieldsets = (
        ('EnglishWord Main', {
            'fields': (('word', 'translation',), 'another_means', ('prefix', 'speech_code')),
        }),
        ('EnglishWord Extra', {
            'classes': ('collapse', ),
            'fields': ('transcription', 'definition', 'examples', ),
        }),
        ('EnglishWord Media', {
            'classes': ('collapse', ),
            'fields': ('image_url', 'sound_url'),
        })
    )
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    class Media:
        js = ['admin/js/load_data_from_api_UI.js',]


@admin.register(FrenchWord)
class FrenchWordAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('word', 'genus', 'translation')
    list_filter = (('genus', ChoiceDropdownFilter),)
    readonly_fields = ('another_means', )
    search_fields = ('word', 'translation')
    fieldsets = (
        ('FrenchWord Main', {
            'fields': (('word', 'translation'), 'another_means', ('genus')),
        }),
        ('FrenchWord Extra', {
            'classes': ('collapse', ),
            'fields': ('examples', ),
        }),
        ('FrenchWord Media', {
            'classes': ('collapse', ),
            'fields': ('image_url', 'sound_url'),
        })
    )
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(IrregularEnglishVerb)
class IrregularEnglishVerbAdmin(admin.ModelAdmin):
    show_full_result_count = False
    autocomplete_fields = ('infinitive', )
    list_display = ('infinitive', 'past_simple', 'past_participle')
    search_fields = ('infinitive__word', 'past_simple', 'past_participle')
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(SpanishWord)
class SpanishWordAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('word', 'translation')
    search_fields = ('word', 'translation')
    readonly_fields = ('another_means', )
    fieldsets = (
        ('SpanishWord Main', {
            'fields': (('word', 'translation',), 'another_means', ('prefix', )),
        }),
        ('SpanishWord Extra', {
            'classes': ('collapse', ),
            'fields': ('transcription', 'definition', 'examples', ),
        }),
        ('SpanishWord Media', {
            'classes': ('collapse', ),
            'fields': ('image_url', 'sound_url'),
        })
    )
    save_as = True

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)