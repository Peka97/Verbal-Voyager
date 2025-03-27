from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.admin.utils import quote

from logger import get_logger


logger = get_logger()
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


class LessonTask(models.Model):
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


class Lesson(models.Model):
    STATUS_CHOICES = (
        ('P', 'Запланировано'),
        ('M', 'Пропущено'),
        ('D', 'Завершено'),
        ('C', 'Отменено')
    )
    title = models.CharField(
        verbose_name='Название урока',
        max_length=50,
        default='English',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время урока'
    )
    duration = models.SmallIntegerField(
        verbose_name='Продолжительность',
        default=60,
        help_text="В минутах"
    )
    is_paid = models.BooleanField(verbose_name="Статус оплаты", default=False)
    status = models.CharField(
        verbose_name="Статус урока",
        max_length=20,
        default='P',
        choices=STATUS_CHOICES
    )
    student_id = models.ForeignKey(
        User,
        related_name='lessons_new_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        on_delete=models.CASCADE,
        verbose_name="Ученик",
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

    def save(self,  *args, **kwargs):
        super().save(*args, **kwargs)
        if self.lesson_plan.first():
            self.lesson_plan.first().save()

    def get_admin_edit_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[quote(self.pk)])

    def get_lesson_time(self):
        time_end = (
            self.datetime +
            timedelta(minutes=self.duration)
        ).strftime('%H:%M')

        return f"{self.datetime.strftime('%d.%m.%Y %H:%M')} - {time_end}"
    get_lesson_time.short_description = 'Время урока'

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
    lesson_1_duration = models.IntegerField(
        verbose_name='Длительность урока',
        default=45,
        help_text='В минутах'
    )
    lesson_2 = models.DateTimeField(
        verbose_name='Время второго урока в неделе',
        null=True,
        blank=True
    )
    lesson_2_duration = models.IntegerField(
        verbose_name='Длительность урока',
        default=45,
        help_text='В минутах'
    )
    lesson_3 = models.DateTimeField(
        verbose_name='Время третьего урока в неделе',
        null=True,
        blank=True
    )
    lesson_3_duration = models.IntegerField(
        verbose_name='Длительность урока',
        default=45,
        help_text='В минутах'
    )
    lesson_4 = models.DateTimeField(
        verbose_name='Время четвертого урока в неделе',
        null=True,
        blank=True
    )
    lesson_4_duration = models.IntegerField(
        verbose_name='Длительность урока',
        default=45,
        help_text='В минутах'
    )
    lesson_5 = models.DateTimeField(
        verbose_name='Время пятого урока в неделе',
        null=True,
        blank=True
    )
    lesson_5_duration = models.IntegerField(
        verbose_name='Длительность урока',
        default=45,
        help_text='В минутах'
    )
    is_active = models.BooleanField(
        verbose_name='Статус',
        default=True
    )
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
