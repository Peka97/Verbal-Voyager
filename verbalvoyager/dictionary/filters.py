from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


# class HasDetailsFilter(admin.SimpleListFilter):
#     title = _('Has details')
#     parameter_name = 'has_details'

#     def lookups(self, request, model_admin):
#         return (
#             ('yes', _('Yes')),
#             ('no', _('No')),
#         )

#     def queryset(self, request, queryset):
#         if self.value() == 'yes':
#             return queryset.filter(
#                 Q(englishworddetail__isnull=False) |
#                 Q(frenchworddetail__isnull=False) |
#                 Q(russianworddetail__isnull=False) |
#                 Q(spanishworddetail__isnull=False)
#             )
#         if self.value() == 'no':
#             return queryset.exclude(
#                 Q(englishworddetail__isnull=False) |
#                 Q(frenchworddetail__isnull=False) |
#                 Q(russianworddetail__isnull=False) |
#                 Q(spanishworddetail__isnull=False)
#             )
#         return queryset


class WordLanguageFilter(admin.SimpleListFilter):
    title = _('Язык слова-источника')
    parameter_name = 'source_lang'

    def lookups(self, request, model_admin):
        from .models import Language
        return Language.objects.exclude(name='Russian').values_list('id', 'name').order_by('name')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source_word__language_id=self.value())
        return queryset


class InvalidWordsFilter(admin.SimpleListFilter):
    title = 'Некорректные слова'
    parameter_name = 'invalid'

    def lookups(self, request, model_admin):
        return (
            ('invalid', 'Некорректные слова'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'invalid':
            return queryset.filter(
                Q(word__contains=' **') |
                Q(word__contains=' *') |
                Q(word__endswith=' ') |
                Q(word__regex=r'[A-ZА-ЯЁ].$') |
                Q(word__regex=r'^[A-ZА-ЯЁ]')
            )
        return queryset
