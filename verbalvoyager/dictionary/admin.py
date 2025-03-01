from django.contrib import admin

from .models import EnglishWord, FrenchWord, IrregularEnglishVerb


@admin.register(EnglishWord)
class WordAdmin(admin.ModelAdmin):
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

    class Media:
        js = ['admin/js/load_data_from_api_UI.js',]


@admin.register(FrenchWord)
class FrenchWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'genus', 'translation')
    list_filter = ['genus', ]
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


@admin.register(IrregularEnglishVerb)
class IrregularEnglishVerbAdmin(admin.ModelAdmin):
    autocomplete_fields = ('infinitive', )
    list_display = ('infinitive', 'past_simple', 'past_participle')
    search_fields = ('infinitive__word', 'past_simple', 'past_participle')
