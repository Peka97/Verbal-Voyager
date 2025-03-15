# -*- coding: utf-8 -*-

from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _, ngettext
from rangefilter.filters import DateRangeFilterBuilder, DateRangeQuickSelectListFilterBuilder

from pages.filters import DropdownFilter, ChoiceDropdownFilter
from .filters import TeachersListFilter, StudentsListFilter
from logger import get_logger
from event_calendar.models import Lesson, Course, Review, ProjectType, Project, ProjectTask, LessonTask
from event_calendar.forms import LessonAdminForm, LessonAdminForm, ProjectAdminForm


logger = get_logger()
User = get_user_model()


class LessonTaskInline(admin.TabularInline):
    model = LessonTask


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    show_full_result_count = False
    form = LessonAdminForm
    ordering = ('-datetime', )
    autocomplete_fields = ('student_id', )
    search_fields = ['student_id', 'lesson_id']
    list_display = ('datetime', 'title', 'status',
                    'is_paid', 'teacher_id', 'student_id')
    list_display_links = ('datetime', 'title')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        ('is_paid', DropdownFilter),
        ('status', ChoiceDropdownFilter),
        ('datetime', DateRangeQuickSelectListFilterBuilder(title='Дата урока')),
    ]
    actions = ['set_pay', 'set_not_pay', 'set_done', 'set_miss', 'set_cancel']
    save_as = True
    inlines = [
        LessonTaskInline,
    ]

    fieldsets = (
        ('Lesson Info', {
            'fields': (('title', 'datetime'), 'student_id', ),
        }),
        ('Lesson Options', {
            'classes': ('collapse', ),
            'fields': (('status', 'is_paid', ), 'teacher_id', 'project_id'),
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('teacher_id', 'student_id')

    def get_form(self, request, obj=None, **kwargs):
        form = super(LessonAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher_id'].initial = request.user
        form.base_fields['teacher_id'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['student_id'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form

    def get_actions(self, request):
        actions = super().get_actions(request)
        delete_action = actions.pop('delete_selected')
        actions['delete_selected'] = delete_action

        return actions

    @admin.action(description='Изменить статус на "Оплачено"')
    def set_pay(self, request, queryset):
        for obj in queryset:
            if not obj.is_paid:
                obj.is_paid = True
                obj.save()

    @admin.action(description='Изменить статус на "Не оплачено"')
    def set_not_pay(self, request, queryset):
        for obj in queryset:
            if obj.is_paid:
                obj.is_paid = False
                obj.save()

    @admin.action(description='Проставить пропуски')
    def set_miss(self, request, queryset):
        for obj in queryset:
            if obj.status != 'M':
                obj.status = 'M'
                obj.save()

    @admin.action(description='Отменить уроки')
    def set_cancel(self, request, queryset):
        for obj in queryset:
            if obj.status != 'C':
                obj.status = 'C'
                obj.save()

    @admin.action(description='Закончить уроки')
    def set_done(self, request, queryset):
        for obj in queryset:
            if obj.status != 'D':
                obj.status = 'D'
                obj.save()


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('project_id', )
    autocomplete_fields = ('project_id', )
    list_display = ('name', 'points', 'project_id', 'is_completed')
    list_filter = (
        ('is_completed', DropdownFilter),
    )
    actions = ('set_complete', 'unset_complete')
    fieldsets = (
        (u'Task Type', {
            'fields': ('name',),
        }),
        ('Task Target', {
            'description': 'Выбери проект, на которое необходимо добавить задание.',
            'fields': ('project_id', ),
        }),
        ('Task Options', {
            'classes': ('collapse', ),
            'description': 'Выбери опции заданий.',
            'fields': (('points', 'is_completed'),),
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('project_id')

    @admin.action(description='Завершить задачу')
    def set_complete(self, request, queryset):
        for task in queryset:
            task.is_completed = True
            task.save()

    @admin.action(description='Возобновить задачу')
    def unset_complete(self, request, queryset):
        for task in queryset:
            task.is_completed = False
            task.save()


@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('name', 'points', 'lesson_id', 'is_completed')
    list_filter = (
        ('is_completed', DropdownFilter),
    )
    actions = ('set_complete', 'unset_complete')

    fieldsets = (
        (u'Task Type', {
            'description': 'Опиши суть задания:',
            'fields': ('name',),
        }),
        ('Task Target', {
            'description': 'Выбери урок, на которое необходимо добавить задание.',
            'fields': ('lesson_id',),
        }),
        ('Task Options', {
            'classes': ('collapse', ),
            'fields': (('points', 'is_completed'),),
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('lesson_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "lesson_id":
            kwargs["queryset"] = Lesson.objects.prefetch_related(
                'student_id').all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.action(description='Завершить задачу')
    def set_complete(self, request, queryset):
        for task in queryset:
            task.is_completed = True
            task.save()

    @admin.action(description='Возобновить задачу')
    def unset_complete(self, request, queryset):
        for task in queryset:
            task.is_completed = False
            task.save()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    show_full_result_count = False
    form = ProjectAdminForm

    search_fields = ['students', 'project_id', 'project_type']
    autocomplete_fields = ('students', 'types')

    # filter_horizontal = ('students', 'types',)
    readonly_fields = ('progress', )
    list_display = ('is_active', 'name', 'course_id',
                    'teacher_id', 'get_students', 'from_date', 'to_date', 'progress')
    list_display_links = ('name', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        ('from_date', DateRangeFilterBuilder(title='Дата начала проекта')),
        ('to_date', DateRangeFilterBuilder(title='Дата окончания проекта')),
    ]
    actions = ['create_lessons', ]

    save_as = True
    inlines = [
        ProjectTaskInline,
    ]

    fieldsets = (
        (u'Project Type', {
            'description': 'Укажи название проекта, его курс и тип.',
            'fields': (('name', 'course_id'), 'types'),
        }),
        ('Project Target', {
            'description': 'Выбери студента и учителя, к которым относится проект.',
            'fields': ('students', 'teacher_id'),
        }),
        ('Project Date', {
            'description': 'Выбери даты начала и окончания проекта. Затем, в соответствии с кратностью занятий в неделю, укажи даты ближайших занятий.',
            'fields': (
                ('from_date', 'to_date'),
                'lesson_1', 'lesson_2', 'lesson_3', 'lesson_4', 'lesson_5'
            )
        }),
        ('Project Options', {
            'classes': ('collapse', ),
            'fields': ('is_active',),
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('teacher_id', 'course_id').prefetch_related('students')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tasks":
            kwargs["queryset"] = ProjectTask.objects.all(
            ).prefetch_related('student_id')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher_id'].initial = request.user
        form.base_fields['teacher_id'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        form.base_fields['students'].queryset = User.objects.filter(
            groups__name__in=['Student'])

        return form

    @admin.action(description='Распланировать занятия')
    def create_lessons(self, request, queryset):
        in_period = True
        lessons_created_count = 0

        for project in queryset:
            students = project.students
            teacher = project.teacher_id
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
                    if from_date <= day.date() <= to_date:
                        is_created = self._create(day, students, teacher)

                        if is_created:
                            lessons_created_count += 1

                        days[idx] = day + timedelta(days=7)
                    else:
                        in_period = False
                        break

        self.message_user(
            request,
            ngettext(
                "%d уроков успешно добавлено!",
                "%d урок успешно добавлен!",
                lessons_created_count,
            )
            % lessons_created_count,
            messages.SUCCESS,
        )

    def _create(self, day, students, teacher):
        for student_id in students.all():
            lesson, is_created = Lesson.objects.get_or_create(
                datetime=day,
                student_id=student_id,
                teacher_id=teacher,
            )

            if is_created:
                lesson.save()
        return True


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('course', 'from_user', 'text', 'created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('course', 'from_user')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    show_full_result_count = False


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('id', )
