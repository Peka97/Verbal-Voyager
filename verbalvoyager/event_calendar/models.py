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
        verbose_name='Название курса',
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
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


class Lesson(models.Model):
    title = models.CharField(
        verbose_name='Название урока',
        max_length=50, 
        default='English',
        help_text="Поле заполняется автоматически, если остаётся пустым"
        )
    description = models.TextField(
        verbose_name='Описание урока',
        max_length=255, 
        blank=True, 
        null=True
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
    students = models.ManyToManyField(
        User, related_name='student_lessons', verbose_name="Ученики")
    teacher = models.ForeignKey(
        User, 
        verbose_name="Учитель",
        on_delete=models.CASCADE, 
        related_name='teacher_lessons', 
        null=True)

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
    project = models.CharField(
        max_length=50,
        verbose_name="Название проекта",
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Тип курса',
        on_delete=models.CASCADE,
        related_name='projects',
        blank=False,
        null=False
    )
    type = models.ManyToManyField(
        ProjectType,
        verbose_name='Тип проекта'
    )
    students = models.ManyToManyField(
        User,
        verbose_name='Студенты'
    )
    teacher = models.ForeignKey(
        User,
        verbose_name='Учитель',
        on_delete=models.CASCADE,
        related_name='project_teacher',
        null=True
    )
    from_date = models.DateField(
        verbose_name='Дата начала курса',
        null=False,
        blank=False,
    )
    to_date = models.DateField(
        verbose_name='Дата окончания курса',
        null=False,
        blank=False
        )
    lesson_1 = models.DateTimeField(
        verbose_name='Время первого урока в неделе',
        null=True, 
        blank=True,
        help_text='Укажите в каждом следующем поле в какой ближайший день на неделе и в какое время будет урок.',
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
        verbose_name='Статус активности', 
        default=True
        )

    def __str__(self):
        return self.project

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
