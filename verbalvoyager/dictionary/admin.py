from django.contrib import admin

from .models import EnglishWord, FrenchWord

@admin.register(EnglishWord)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translate')
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