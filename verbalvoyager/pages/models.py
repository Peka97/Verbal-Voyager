from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class ProjectType(models.Model):
    type_name = models.CharField('Тип курса', max_length=50)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = 'Тип курса'
        verbose_name_plural = 'Типы курсов'


class Project(models.Model):
    course_name = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course'
    )
    type_name = models.ForeignKey(
        ProjectType,
        on_delete=models.CASCADE,
        related_name='type'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student'
    )
    from_date = models.DateField(
        auto_now_add=True,
        blank=True
    )
    to_date = models.DateField(
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        print(dir(self.student))
        if self.student.first_name and self.student.last_name:
            return f'{self.course_name} - {self.type_name} - {self.student.last_name} {self.student.first_name}'
        else:
            return f'{self.course_name} - {self.type_name} - {self.student.username}'
        # return f'{self.course_name} - {self.type_name} - {self.student.username}'

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Review(models.Model):
    course_name = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_name',
        null=True
    )
    text = models.CharField(max_length=150)
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='from_user'
    )
    datetime = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self) -> str:
        return f'{self.pk} - {self.datetime.strftime("%d.%m.%Y")} - {self.from_user.first_name}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
