# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.urls import path, reverse
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import Lesson, Course, Review, ProjectType, Project, ProjectTask, LessonTask
from .forms import LessonAdminForm, LessonAdminForm, ProjectAdminForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import ngettext


log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(DEBUG_LOGGING_FP)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

User = get_user_model()


# Filters
class TeachersListFilter(admin.SimpleListFilter):
    title = _("Учитель")
    parameter_name = "teacher"

    def lookups(self, request, model_admin):
        teachers = User.objects.filter(groups__name='Teacher')

        return [
            (teacher.pk, _(f'{teacher.last_name} {teacher.first_name}'))
            for teacher in teachers
        ]

    def queryset(self, request, queryset):
        return queryset.filter(teacher_id=self.value()) if self.value() else None


class StudentsListFilter(admin.SimpleListFilter):
    title = _("Ученик")
    parameter_name = "students"

    def lookups(self, request, model_admin):
        students = User.objects.filter(groups__name='Student')

        return [
            (student.pk, _(f'{student.last_name} {student.first_name}'))
            for student in students
        ]

    def queryset(self, request, queryset):
        return queryset.filter(student_id=self.value()) if self.value() else None


class LessonTaskInline(admin.TabularInline):
    model = LessonTask


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask

# @admin.register(Lesson)
# class LessonAdmin(admin.ModelAdmin):
#     form = LessonAdminForm
#     ordering = ('-datetime', )
#     search_fields = ['student_id', 'lesson_id']
#     filter_horizontal = ('students',)
#     list_display = ('datetime', 'title', 'status',
#                     'is_paid', 'teacher_id', 'get_students')
#     list_display_links = ('datetime', 'title')
#     list_filter = [
#         TeachersListFilter,
#         'datetime',
#         'is_paid',
#         'status',
#         StudentsListFilter,
#     ]
#     actions = ['set_pay', 'set_not_pay', 'set_done', 'set_miss', 'set_cancel']
#     save_as = True
#     # inlines = [
#         # LessonTaskInline,
#     # ]

#     fieldsets = (
#         ('Lesson Info', {
#             'fields': (('title', 'datetime'), 'students', ),
#         }),
#         ('Lesson Options', {
#             'classes': ('collapse', ),
#             'fields': (('status','is_paid', ), 'teacher_id'),
#         })
#     )

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('teacher_id').prefetch_related('students', )

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "tasks":
    #         kwargs["queryset"] = LessonTask.objects.all().prefetch_related('student_id')
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(LessonAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['teacher_id'].initial = request.user
    #     form.base_fields['teacher_id'].queryset = User.objects.filter(groups__name__in=['Teacher'])
    #     form.base_fields['students'].queryset = User.objects.filter(groups__name__in=['Student'])

    #     return form

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     delete_action = actions.pop('delete_selected')
    #     actions['delete_selected'] = delete_action

    #     return actions

    # @admin.action(description='Изменить статус на "Оплачено"')
    # def set_pay(self, request, queryset):
    #     for obj in queryset:
    #         if not obj.is_paid:
    #             obj.is_paid = True
    #             obj.save()

    # @admin.action(description='Изменить статус на "Не оплачено"')
    # def set_not_pay(self, request, queryset):
    #     for obj in queryset:
    #         if obj.is_paid:
    #             obj.is_paid = False
    #             obj.save()

    # @admin.action(description='Проставить пропуски')
    # def set_miss(self, request, queryset):
    #     for obj in queryset:
    #         if obj.status != 'M':
    #             obj.status = 'M'
    #             obj.save()

    # @admin.action(description='Отменить уроки')
    # def set_cancel(self, request, queryset):
    #     for obj in queryset:
    #         if obj.status != 'C':
    #             obj.status = 'C'
    #             obj.save()

    # @admin.action(description='Закончить уроки')
    # def set_done(self, request, queryset):
    #     for obj in queryset:
    #         if obj.status!= 'D':
    #             obj.status = 'D'
    #             obj.save()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    ordering = ('-datetime', )
    autocomplete_fields = ('student_id', )
    search_fields = ['student_id', 'lesson_id']
    list_display = ('datetime', 'title', 'status',
                    'is_paid', 'teacher_id', 'student_id')
    list_display_links = ('datetime', 'title')
    list_filter = [
        TeachersListFilter,
        'datetime',
        'is_paid',
        'status',
        StudentsListFilter,
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
    search_fields = ('project_id', )
    autocomplete_fields = ('project_id', )
    list_display = ('name', 'points', 'project_id', 'is_completed')
    list_filter = (
        'is_completed',
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
# @admin.register(BaseLessonTask)
# class BaseLessonTaskAdmin(admin.ModelAdmin):
#     list_display = ('name', )


@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    # autocomplete_fields = ('lesson_id', )
    list_display = ('name', 'points', 'lesson_id', 'is_completed')
    list_filter = (
        'is_completed',
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
    form = ProjectAdminForm

    search_fields = ['student_id', 'project_id']
    filter_horizontal = ('students', 'types',)
    readonly_fields = ('progress', )
    list_display = ('is_active', 'name', 'course_id',
                    'teacher_id', 'get_students', 'from_date', 'to_date', 'progress')
    list_display_links = ('name', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
    ]
    actions = ['create_lessons', ]

    save_as = True
    inlines = [
        ProjectTaskInline,
    ]

    fieldsets = (
        (u'Project Type', {
            'description': 'Укажи название проекта, его курс и тип.',
            'fields': ('name', 'course_id', 'types'),
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
    list_display = ('course', 'from_user', 'text', 'created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('course', 'from_user')


admin.site.register(Course)
admin.site.register(ProjectType)
