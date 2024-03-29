from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Word, Exercise, ExerciseResult


User = get_user_model()


# Filters
# class DecadeBornListFilter(admin.SimpleListFilter):
#     # Human-readable title which will be displayed in the
#     # right admin sidebar just above the filter options.
#     title = _("Role")

#     # Parameter for the filter that will be used in the URL query.
#     parameter_name = "role"

#     def lookups(self, request, model_admin):
#         """
#         Returns a list of tuples. The first element in each
#         tuple is the coded value for the option that will
#         appear in the URL query. The second element is the
#         human-readable name for the option that will appear
#         in the right sidebar.
#         """
#         return [
#             ("Student", _("is student")),
#             ("Teacher", _("is teacher")),
#         ]

#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset based on the value
#         provided in the query string and retrievable via
#         `self.value()`.
#         """
#         # Compare the requested value (either '80s' or '90s')
#         # to decide how to filter the queryset.

#         if self.value() == "Teacher":
#             return queryset.filter(
#                 groups__name='Teacher',
#             )
# if self.value() == "90s":
#     return queryset.filter(
#         birthday__gte=date(1990, 1, 1),
#         birthday__lte=date(1999, 12, 31),
#     )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    filter_horizontal = ('words', )
    # list_display = ('name', 'is_active', 'student', 'teacher', 'words')
    # list_display_links = ('name', 'student', 'teacher')
    list_filter = (
        ("teacher", admin.RelatedOnlyFieldListFilter),
        ("student", admin.RelatedOnlyFieldListFilter),
        'is_active'
    )
    search_fields = ('teacher__username', )
    save_as = True
    actions = ['make_active', 'make_inactive']

    @admin.action(description='Активировать')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивировать')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    search_fields = ('word', 'translate')


admin.site.register(ExerciseResult)
