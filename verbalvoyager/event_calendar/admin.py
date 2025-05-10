import logging
from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.translation import ngettext
from rangefilter.filters import DateRangeFilterBuilder, DateRangeQuickSelectListFilterBuilder
from nested_admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline

from .filters import TeachersListFilter, StudentsListFilter
from pages.filters import DropdownFilter, ChoiceDropdownFilter
from event_calendar.models import Lesson, Course, Review, ProjectType, Project, ProjectTask, LessonTask
from event_calendar.forms import LessonAdminForm, ProjectAdminForm
from lesson_plan.models import EnglishLessonPlan
from lesson_plan.admin import EnglishLessonPlanAdmin
from exercises.models import ExerciseEnglishWords
from logging_app.helpers import log_action


logger = logging.getLogger('django')
User = get_user_model()


class LessonTaskInline(NestedTabularInline):
    model = LessonTask
    extra = 0


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0


class EnglishLessonPlanInline(NestedStackedInline):
    model = EnglishLessonPlan
    extra = 0
    min_num = 1
    max_num = 1
    autocomplete_fields = ('new_vocabulary', )
    fieldsets = EnglishLessonPlanAdmin.fieldsets
    inlines = EnglishLessonPlanAdmin.inlines


@admin.register(Lesson)
class LessonAdmin(NestedModelAdmin):
    show_full_result_count = False
    form = LessonAdminForm
    ordering = ('-datetime', )
    autocomplete_fields = ('student_id', )
    search_fields = ['id', 'student_id__last_name', 'student_id__first_name']
    list_display = ('get_lesson_time', 'title', 'status',
                    'is_paid', 'teacher_id', 'student_id')
    list_display_links = ('get_lesson_time', 'title')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter,
        ('is_paid', DropdownFilter),
        ('status', ChoiceDropdownFilter),
        ('datetime', DateRangeQuickSelectListFilterBuilder(title='Дата урока')),
    ]
    actions = ['set_pay', 'set_not_pay', 'set_done', 'set_miss', 'set_cancel',
               'set_duration_45', 'set_duration_60', 'set_duration_90',]
    save_as = True
    inlines = [
        LessonTaskInline,
        EnglishLessonPlanInline,
    ]

    fieldsets = (
        ('Lesson Info', {
            'fields': (('title', 'datetime', 'duration'), 'student_id', ),
        }),
        ('Lesson Options', {
            'classes': ('collapse', ),
            'fields': (('status', 'is_paid', ), 'teacher_id', 'project_id'),
        })
    )

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        for formset in formsets:
            if formset.model is EnglishLessonPlan and formset.forms[0].is_valid():
                lesson_plan_form = formset.forms[0]

                lesson_plan = lesson_plan_form.save(commit=False)
                exercise_id = lesson_plan.exercise_id

                words_queryset = lesson_plan_form.cleaned_data.get(
                    'new_vocabulary')

                if not words_queryset:
                    lesson_plan.exercise_id = None

                if exercise_id:
                    current_words = set(exercise_id.words.all())

                    new_words = set(words_queryset.all())

                    if len(current_words) != len(new_words) or any(word not in current_words for word in new_words):
                        exercise_id.words.set(new_words)
                        exercise_id.save()

                else:
                    if words_queryset.exists():
                        new_exercise = ExerciseEnglishWords.objects.create(
                            name=f"New vocabulary \"{lesson_plan_form.cleaned_data.get('lesson_id').title}\"",
                            student=lesson_plan.lesson_id.student_id,
                            teacher=lesson_plan.lesson_id.teacher_id,
                            is_active=True,
                        )
                        new_exercise.save()
                        new_exercise.words.set(words_queryset.all())

                        lesson_plan.save()
                        lesson_plan.exercise_id = new_exercise

                lesson_plan.save()

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

    @admin.action(description='Задать длительность урока 45 минут')
    def set_duration_45(self, request, queryset):
        for obj in queryset:
            obj.duration = 45
            obj.save()

    @admin.action(description='Задать длительность урока 60 минут')
    def set_duration_60(self, request, queryset):
        for obj in queryset:
            obj.duration = 60
            obj.save()

    @admin.action(description='Задать длительность урока 90 минут')
    def set_duration_90(self, request, queryset):
        for obj in queryset:
            obj.duration = 90
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

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

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

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

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

    search_fields = ['name', 'students__last_name']
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

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

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
            durations = []

            if project.lesson_1:
                days.append(project.lesson_1)
                durations.append(project.lesson_1_duration)

            if project.lesson_2:
                days.append(project.lesson_2)
                durations.append(project.lesson_2_duration)

            if project.lesson_3:
                days.append(project.lesson_3)
                durations.append(project.lesson_3_duration)

            if project.lesson_4:
                days.append(project.lesson_4)
                durations.append(project.lesson_4_duration)

            if project.lesson_5:
                days.append(project.lesson_5)
                durations.append(project.lesson_5_duration)

            while in_period:

                for idx, day in enumerate(days):
                    if from_date <= day.date() <= to_date:
                        lesson_duration = durations[idx % len(durations)]
                        is_created = self._create(
                            day, lesson_duration, students, teacher)

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

    def _create(self, day, lesson_duration, students, teacher):
        for student_id in students.all():
            lesson, is_created = Lesson.objects.get_or_create(
                datetime=day,
                duration=lesson_duration,
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

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('course', 'from_user')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    show_full_result_count = False

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('id', )

    @log_action
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)
