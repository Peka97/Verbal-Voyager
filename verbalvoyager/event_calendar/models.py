import logging
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import pre_save, post_save, m2m_changed, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.admin.utils import quote

from verbalvoyager.settings import DEBUG_LOGGING_FP


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(DEBUG_LOGGING_FP))

User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Review(models.Model):
    course = models.ForeignKey(
        Course,
        verbose_name='Название курса',
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,  # TODO: remove?
        null=True,  # TODO: remove?
    )
    text = models.TextField(
        verbose_name='Отзыв',
        max_length=500
    )
    from_user = models.ForeignKey(
        User,
        verbose_name='Имя пользователя',
        on_delete=models.CASCADE,
        related_name='review_from_user'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        editable=True,
        null=True,
        blank=True
    )

    def get_created_at(self):
        return self.created_at.strftime("%d.%m.%Y")

    get_created_at.short_description = 'Дата создания'

    def __str__(self) -> str:
        return f'{self.pk} - {self.created_at.strftime("%d.%m.%Y")} - {self.course.name} - {self.from_user.first_name}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

# class BaseLessonTask(models.Model):
#     name = models.CharField(
#         max_length=50,
#         verbose_name='Название обычного задания'
#     )
#     def __str__(self) -> str:
#         return self.name

#     def __repr__(self) -> str:
#         return f"{self.name} [id:{self.pk}]"

#     class Meta:
#         verbose_name = 'Обычное задание'
#         verbose_name_plural = 'Обычные задания'


class LessonTask(models.Model):
    # base_name = models.ForeignKey(
    #     BaseLessonTask,
    #     on_delete=models.CASCADE,
    #     related_name='task_basename',
    #     blank=True,
    #     null=True,
    #     verbose_name='Обычное задание',
    #     help_text="Выберите обычное задание из предложенных. Поле с уникальным заданием необходимо оставить пустым."
    # )
    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя задания урока',
        help_text="Опиши задание, которое необходимо выполнить ученику."
    )
    points = models.SmallIntegerField(
        verbose_name='Баллы',
        default=1,
    )
    is_completed = models.BooleanField(
        verbose_name='Задача завершена',
        default=False,
    )
    # lesson_id = models.ForeignKey(
    #     'Lesson',
    #     verbose_name='Урок',
    #     on_delete=models.CASCADE,
    #     related_name='lesson_tasks',
    #     blank=True,
    #     null=True
    # )
    lesson_id = models.ForeignKey(
        'Lesson',
        verbose_name='Урок',
        on_delete=models.CASCADE,
        related_name='lesson_tasks',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name if self.name else 'None'

    def __repr__(self):
        return f"{self.__str__()} [Lesson: {self.pk}]"

    class Meta:
        verbose_name = 'Задача урока'
        verbose_name_plural = 'Задачи урока'

# class Lesson(models.Model):
#     title = models.CharField(
#         verbose_name='Название урока',
#         max_length=50,
#         default='English',
#         help_text="Поле заполняется автоматически, если остаётся пустым"
#     )
#     datetime = models.DateTimeField(
#         verbose_name='Дата и время урока'
#     )
#     is_paid = models.BooleanField(verbose_name="Статус оплаты", default=False)
#     status = models.CharField(
#         verbose_name="Статус урока",
#         max_length=20,
#         default='P',
#         choices=[
#             ('P', 'Запланировано'),
#             ('M', 'Пропущено'),
#             ('D', 'Завершено'),
#             ('C', 'Отменено')
#         ]
#     )
#     students = models.ManyToManyField(
#         User,
#         related_name='student_lessons',
#         limit_choices_to={'groups__name__in': ['Student', ]},
#         verbose_name="Ученики"
#     )
#     teacher_id = models.ForeignKey(
#         User,
#         verbose_name="Учитель",
#         limit_choices_to={'groups__name__in': ['Teacher', ]},
#         on_delete=models.CASCADE,
#         related_name='teacher_lessons',
#         null=True
#     )

#     def __str__(self):
#         return f"{self.datetime.strftime('%d.%m.%Y %H:%M')} | {self.get_students()} [{self.title}]"

#     def get_students(self):
#         # try:
#         #     students = [f'{student.last_name} {student.first_name}' for student in tuple(
#         #         self.students.all())]
#         #     return ', '.join(students)
#         # except Exception as err:
#         #     logger.error(err)
#         return self.students

#     get_students.short_description = students.verbose_name

#     class Meta:
#         verbose_name = 'Занятие'
#         verbose_name_plural = 'Занятия'

#         ordering = ['datetime']


class Lesson(models.Model):
    title = models.CharField(
        verbose_name='Название урока',
        max_length=50,
        default='English',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время урока'
    )
    is_paid = models.BooleanField(verbose_name="Статус оплаты", default=False)
    status = models.CharField(
        verbose_name="Статус урока",
        max_length=20,
        default='P',
        choices=[
            ('P', 'Запланировано'),
            ('M', 'Пропущено'),
            ('D', 'Завершено'),
            ('C', 'Отменено')
        ]
    )
    student_id = models.ForeignKey(
        User,
        related_name='lessons_new_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        on_delete=models.CASCADE,
        verbose_name="Ученики",
        null=True
    )
    teacher_id = models.ForeignKey(
        User,
        verbose_name="Учитель",
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        on_delete=models.CASCADE,
        related_name='lessons_new_teacher',
        null=True
    )
    project_id = models.ForeignKey(
        'Project',
        verbose_name='Проект',
        on_delete=models.CASCADE,
        related_name='lessons_new_project',
        blank=True,
        null=True
    )

    def get_admin_edit_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[quote(self.pk)])

    # def __str__(self):
    #     return f"{self.datetime.strftime('%d.%m.%Y %H:%M')} | {self.get_students()} [{self.title}]"

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'

        ordering = ['-datetime']


class ProjectTask(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название задачи'
    )
    points = models.SmallIntegerField(
        verbose_name='Баллы',
        default=1,
    )
    is_completed = models.BooleanField(
        verbose_name='Задача завершена',
        default=False,
    )
    project_id = models.ForeignKey(
        'Project',
        verbose_name='Проект',
        on_delete=models.CASCADE,
        related_name='project_task',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        projects = Project.objects.filter(tasks=self.pk)
        for project in projects:
            project.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [Project: {self.project_id}]"

    class Meta:
        verbose_name = 'Задача проекта'
        verbose_name_plural = 'Задачи проекта'


class ProjectType(models.Model):
    name = models.CharField('Тип проекта', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип проекта'
        verbose_name_plural = 'Типы проектов'


class Project(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Название проекта",
        blank=True,
        null=True
    )
    course_id = models.ForeignKey(
        Course,
        verbose_name='Тип курса',
        on_delete=models.CASCADE,
        related_name='projects',
        blank=True,
        null=True
    )
    types = models.ManyToManyField(
        ProjectType,
        verbose_name='Тип проекта'
    )
    students = models.ManyToManyField(
        User,
        verbose_name='Студенты',
        limit_choices_to={'groups__name__in': ['Student', ]},
    )
    teacher_id = models.ForeignKey(
        User,
        verbose_name='Учитель',
        on_delete=models.CASCADE,
        related_name='project_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True
    )
    from_date = models.DateField(
        verbose_name='Дата начала',
        null=True,
        blank=True,
    )
    to_date = models.DateField(
        verbose_name='Дата окончания',
        null=True,
        blank=True
    )
    lesson_1 = models.DateTimeField(
        verbose_name='Время первого урока в неделе',
        null=True,
        blank=True,
    )
    lesson_2 = models.DateTimeField(
        verbose_name='Время второго урока в неделе',
        null=True,
        blank=True
    )
    lesson_3 = models.DateTimeField(
        verbose_name='Время третьего урока в неделе',
        null=True,
        blank=True
    )
    lesson_4 = models.DateTimeField(
        verbose_name='Время четвертого урока в неделе',
        null=True,
        blank=True
    )
    lesson_5 = models.DateTimeField(
        verbose_name='Время пятого урока в неделе',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name='Статус',
        default=True
    )
    # tasks = models.ManyToManyField(
    #     ProjectTask,
    #     verbose_name='Задачи проекта',
    # )
    progress = models.SmallIntegerField(
        verbose_name='Прогресс проекта',
        default=0,
        auto_created=True,
        help_text='От 0 до 100'
    )

    def set_progress(self):
        if self.tasks.count() > 0:
            self.progress = self.tasks.filter(
                is_completed=False).count() * 100 / self.tasks.count()
        else:
            self.progress = 0

    def get_students(self):
        try:
            students = [f'{student.last_name} {student.first_name}' for student in tuple(
                self.students.all())]
            return ', '.join(students)
        except Exception as err:
            logger.error(err)
            return self.student

    get_students.short_description = students.verbose_name

    def __str__(self):
        return self.name if self.name else 'None'

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
