import logging
from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import Lesson, Course, Review, ProjectType, Project, ProjectTask, LessonTask
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
        return queryset.filter(students=self.value()) if self.value() else None


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    ordering = ('-datetime', )
    filter_horizontal = ('students', 'tasks')
    list_display = ('datetime', 'title', 'status',
                    'is_paid', 'teacher_id', 'get_students')
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
        form.base_fields['teacher_id'].initial = request.user
        form.base_fields['teacher_id'].queryset = User.objects.filter(groups__name__in=['Teacher'])
        form.base_fields['students'].queryset = User.objects.filter(groups__name__in=['Student'])
        
        return form
    
    def save_related(self, request, form, formsets, change):
        cleaned_data = form.cleaned_data
        tasks = cleaned_data.get('tasks')
        
        homework_task = tasks.filter(
            name='Выполнить домашнее задание',
            points=1,
        )
        
        if not homework_task.exists():
            students = cleaned_data.get('students')
            
            for student in students:
                new_task = LessonTask.objects.create(
                        name='Выполнить домашнее задание',
                        points=1,
                        student_id=student
                        )
                cleaned_data['tasks'] = tasks.union(LessonTask.objects.filter(pk=new_task.pk))        
        
        super(LessonAdmin, self).save_related(request, form, formsets, change)
    
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
            if obj.status!= 'D':
                obj.status = 'D'
                obj.save()

@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'points', 'student_id', 'is_completed')
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

@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'points', 'student_id', 'is_complete')
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

    filter_horizontal = ('students', 'types', 'tasks')
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
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['teacher_id'].initial = request.user
        form.base_fields['teacher_id'].queryset = User.objects.filter(groups__name__in=['Teacher'])
        form.base_fields['students'].queryset = User.objects.filter(groups__name__in=['Student'])
        
        return form

    @admin.action(description='Распланировать занятия')
    def create_lessons(self, request, queryset):
        in_period = True

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
                        self._create(day, students, teacher)
                        days[idx] = day + timedelta(days=7)
                    else:
                        in_period = False
                        break

    def _create(self, day, students, teacher):
        lesson, is_created = Lesson.objects.get_or_create(
            datetime=day,
            teacher_id=teacher
        )
        
        if is_created:

            for student in list(students.all()):
                lesson.students.add(student)
                
                homework_task = LessonTask.objects.create(
                    name='Выполнить домашнее задание',
                    points=1,
                    student=student
                    )
            
                lesson.tasks.add(homework_task)

            lesson.save()
        else:
            lesson = Lesson.objects.filter(datetime=day, teacher_id=teacher)

            for student in list(students.all()):
                new_lesson = lesson.filter(students=student)

                if not new_lesson:
                    lesson = Lesson.objects.filter(
                        datetime=day, teacher_id=teacher).first()
                    lesson.students.add(student)
                    
                else:
                    lesson = new_lesson
                
                lesson.save()


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_created_at', 'from_user', 'course', 'text')

admin.site.register(Course)
admin.site.register(ProjectType)
