import logging
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

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
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=False,
        null=False
    )
    text = models.TextField(max_length=500)
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_from_user'
    )
    created_at = models.DateTimeField(
        editable=True,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.pk} - {self.created_at.strftime("%d.%m.%Y")} - {self.course.name} - {self.from_user.first_name}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Lesson(models.Model):
    title = models.CharField(max_length=50, default='English')
    description = models.TextField(max_length=255, blank=True, null=True)
    datetime = models.DateTimeField()
    is_paid = models.BooleanField(verbose_name="Оплачено", default=False)
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        default='P',
        choices=[
            ('P', 'Запланировано'),
            ('M', 'Пропущено'),
            ('D', 'Завершено'),
            ('C', 'Отменено')
        ]
    )
    students = models.ManyToManyField(
        User, related_name='student_lessons', verbose_name="Ученики")
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='teacher_lessons', null=True)

    def __str__(self):
        return f'{self.pk} - {self.datetime} - {list(self.students.all())} - {self.title}'

    def get_students(self):
        try:
            students = [f'{student.last_name} {student.first_name}' for student in list(
                self.students.all())]
            return ', '.join(students)
        except Exception as err:
            logger.error(err)
            return self.student
    get_students.short_description = students.verbose_name

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'

        ordering = ['-datetime']


class ProjectType(models.Model):
    type_name = models.CharField('Тип проекта', max_length=50)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = 'Тип проекта'
        verbose_name_plural = 'Типы проектов'


class Project(models.Model):
    project_name = models.CharField(
        max_length=50,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='projects',
        blank=False,
        null=False
    )
    type = models.ManyToManyField(
        ProjectType,
        verbose_name='Тип'
    )
    students = models.ManyToManyField(
        User,
        verbose_name='Студенты'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher',
        null=True
    )
    from_date = models.DateField(
        null=False,
        blank=False,
    )
    to_date = models.DateField(null=False, blank=False)
    lesson_1 = models.DateTimeField(null=True, blank=True)
    lesson_2 = models.DateTimeField(null=True, blank=True)
    lesson_3 = models.DateTimeField(null=True, blank=True)
    lesson_4 = models.DateTimeField(null=True, blank=True)
    lesson_5 = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
