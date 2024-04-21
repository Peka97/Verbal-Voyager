import logging

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.html import format_html


from .models import Word, Exercise, ExerciseResult
from .forms import ExerciseAdminForm


logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.addHandler(logging.FileHandler(
    '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
)

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
            if len(queryset) >= 1 and isinstance(queryset[0], ExerciseResult):
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
            if len(queryset) >= 1 and isinstance(queryset[0], ExerciseResult):
                return queryset.filter(
                    exercise__student=self.value()
                )
            else:
                return queryset.filter(
                    student=self.value()
                )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    form = ExerciseAdminForm

    filter_horizontal = ('words', )
    list_display = ('is_active', 'name', 'student', 'teacher', 'get_words')
    list_display_links = ('name', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        'is_active'
    ]
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
    list_display = ('lang', 'word', 'translate')
    list_filter = ['lang', ]
    search_fields = ('word', 'translate')


@admin.register(ExerciseResult)
class ExerciseResultAdmin(admin.ModelAdmin):
    list_display = ('get_ex_name', 'get_teacher', 'get_student',
                    'step_1', 'step_2', 'step_3', 'step_4')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]
    # search_fields = ('exercise.name')
