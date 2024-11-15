import logging
from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import Lesson, Course, Review, ProjectType, Project, Task
from .forms import LessonAdminForm, ProjectAdminForm
from django.contrib.auth import get_user_model


log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(DEBUG_LOGGING_FP)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

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
            return queryset.filter(
                teacher=self.value()
            )


class StudentsListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Ученик")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "students"

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
            return queryset.filter(
                students=self.value()
            )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    ordering = ('-datetime', )
    filter_horizontal = ('students', )
    list_display = ('datetime', 'title', 'status',
                    'is_paid', 'teacher', 'get_students')
    list_display_links = ('datetime', 'title')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        'datetime',
        'is_paid',
        'status',
    ]
    actions = ['set_pay', 'set_not_pay', 'set_done', 'set_miss', 'set_cancel']
    save_as = True
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(LessonAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(groups__name__in=['Teacher'])
        form.base_fields['students'].queryset = User.objects.filter(groups__name__in=['Student'])
        
        return form

    @admin.action(description='Изменить статус на "Оплачено"')
    def set_pay(self, request, queryset):
        for obj in queryset:
            obj.is_paid = True
            obj.save()

    @admin.action(description='Изменить статус на "Не оплачено"')
    def set_not_pay(self, request, queryset):
        for obj in queryset:
            obj.is_paid = False
            obj.save()

    @admin.action(description='Проставить пропуски')
    def set_miss(self, request, queryset):
        for obj in queryset:
            obj.status = 'M'
            obj.save()

    @admin.action(description='Отменить уроки')
    def set_cancel(self, request, queryset):
        for obj in queryset:
            obj.status = 'C'
            obj.save()

    @admin.action(description='Закончить уроки')
    def set_done(self, request, queryset):
        for obj in queryset:
            obj.status = 'D'
            obj.save()

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'points', 'student', 'is_complete')
    list_filter = (
        StudentsListFilter,
    )
    actions = ('set_complete', 'unset_complete')
    @admin.action(description='Завершить задачу')
    def set_complete(self, request, queryset):
        for task in queryset:
            task.is_complete = True
            task.save()
    
    @admin.action(description='Возобновить задачу')
    def unset_complete(self, request, queryset):
        for task in queryset:
            task.is_complete = False
            task.save()
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm

    filter_horizontal = ('students', 'type', 'tasks')
    readonly_fields = ('progress', )
    list_display = ('is_active', 'project', 'course',
                    'teacher', 'get_students', 'from_date', 'to_date', 'progress')
    list_display_links = ('project', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]
    actions = ['create_lessons', ]

    save_as = True
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher'].initial = request.user
        form.base_fields['teacher'].queryset = User.objects.filter(groups__name__in=['Teacher'])
        form.base_fields['students'].queryset = User.objects.filter(groups__name__in=['Student'])
        
        return form

    @admin.action(description='Распланировать занятия')
    def create_lessons(self, request, queryset):
        in_period = True

        for project in queryset:
            students = project.students
            teacher = project.teacher
            from_date = project.from_date
            to_date = project.to_date
            days = []

            if project.lesson_1:
                days.append(project.lesson_1)

            if project.lesson_2:
                days.append(project.lesson_2)

            if project.lesson_3:
                days.append(project.lesson_3)

            if project.lesson_4:
                days.append(project.lesson_4)

            if project.lesson_5:
                days.append(project.lesson_5)

            while in_period:

                for idx, day in enumerate(days):
                    logger.info(f"{from_date} {day.date()} {to_date}")
                    logger.info(from_date < day.date() < to_date)

                    if from_date <= day.date() <= to_date:
                        self._create(day, students, teacher)
                        days[idx] = day + timedelta(days=7)
                    else:
                        in_period = False
                        break

    def _create(self, day, students, teacher):
        lesson, is_created = Lesson.objects.get_or_create(
            datetime=day,
            teacher=teacher
        )

        if is_created:

            for student in list(students.all()):
                lesson.students.add(student)

            lesson.save()
        else:
            lesson = Lesson.objects.filter(datetime=day, teacher=teacher)

            for student in list(students.all()):
                new_lesson = lesson.filter(students=student)

                if not new_lesson:
                    lesson = Lesson.objects.filter(
                        datetime=day, teacher=teacher).first()
                    lesson.students.add(student)
                    lesson.save()
                else:
                    lesson = new_lesson

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_created_at', 'from_user', 'course', 'text')

admin.site.register(Course)
admin.site.register(ProjectType)
