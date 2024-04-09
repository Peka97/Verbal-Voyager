import logging
from datetime import datetime, timedelta

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Lesson, Course, Review, ProjectType, Project
from .forms import LessonAdminForm, ProjectAdminForm
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)
logger.level = logging.INFO
logger.addHandler(logging.FileHandler(
    '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
)


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
    filter_horizontal = ('students', )
    list_display = ('pk', 'title', 'status', 'teacher', 'get_students')
    list_display_links = ('pk', 'title')
    list_filter = [
        TeachersListFilter,
        StudentsListFilter
    ]
    save_as = True
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    
    filter_horizontal = ('students', )
    list_display = ('is_active', 'project_name', 'course_name', 'teacher', 'from_date', 'to_date')
    list_display_links = ('project_name', )
    list_filter = [
        TeachersListFilter,
        StudentsListFilter
    ]
    actions = ['create_lessons', ]

    save_as = True
    
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
                self._create(days, students, teacher)

                for idx, day in enumerate(days):
                    days[idx] = day + timedelta(days=7)
                    if not from_date < day.date() < to_date:
                        in_period = False
                        self._create(days, students, teacher)
                        break
        
    def _create(self, days, students, teacher):
        for day in days:
            lesson, is_created = Lesson.objects.get_or_create(
                datetime=day,
                teacher=teacher
            )
            
            if is_created:
                for student in list(students.all()):
                    logger.info(student)
                    lesson.students.add(student)
                lesson.save()
            else:
                logger.info('Lesson was not created')
                lesson = Lesson.objects.filter(datetime=day, teacher=teacher)
                
                for student in list(students.all()):
                    new_lesson = lesson.filter(students=student)
                    logger.info(new_lesson)
                    
                    if not new_lesson:
                        logger.info(f'{student} not in lesson')
                        
                        lesson = Lesson.objects.filter(datetime=day, teacher=teacher).first()
                        lesson.students.add(student)
                        lesson.save()
                    else:
                        lesson = new_lesson
            

admin.site.register(Course)
admin.site.register(Review)
admin.site.register(ProjectType)
