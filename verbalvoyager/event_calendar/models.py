import logging

from django.db import models
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(
    '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
)

User = get_user_model()


class Lesson(models.Model):
    title = models.CharField(max_length=50, default='English')
    description = models.TextField(max_length=255, null=True)
    datetime = models.DateTimeField()
    is_paid = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        default='P',
        choices=[
            ('P', 'planned'),
            ('M', 'missed'),
            ('D', 'done'),
            ('C', 'canceled')
        ]
    )
    students = models.ManyToManyField(
        User, verbose_name="Ученики")
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lesson_teacher', null=True, default=User.objects.get(username='Elizabeth').pk)

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
