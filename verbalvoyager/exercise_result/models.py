import logging

from django.db import models

from exercises.models import ExerciseWords, ExerciseDialog, ExerciseIrregularEnglishVerb

logger = logging.getLogger('django')


class ExerciseWordsResult(models.Model):
    exercise = models.ForeignKey(
        ExerciseWords,
        on_delete=models.CASCADE,
        related_name='result',
        null=True,
        blank=True
    )
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_4 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_5 = models.SmallIntegerField(null=True, blank=True, default=None)

    def set_value(self, step_num, value):
        try:
            self.__dict__[step_num] = value
        except KeyError as err:
            logger.error(err)

    def get_student(self):
        return self.exercise.student if self.exercise else 'Unknown'

    def get_teacher(self):

        return self.exercise.teacher if self.exercise else 'Unknown'

    def get_ex_name(self):
        return self.exercise.name if self.exercise else 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат "Слова"'
        verbose_name_plural = 'Результаты "Слова"'


class ExerciseDialogResult(models.Model):
    exercise = models.ForeignKey(
        ExerciseDialog,
        on_delete=models.CASCADE,
        related_name='result',
        null=True,
        blank=True
    )
    points = models.SmallIntegerField(null=True, blank=True)

    def set_value(self, value):
        self.points = value

    def get_student(self):
        return self.exercise.student if self.exercise else 'Unknown'

    def get_teacher(self):
        return self.exercise.teacher if self.exercise else 'Unknown'

    def get_ex_name(self):
        return self.exercise.name if self.exercise else 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат "Диалог"'
        verbose_name_plural = 'Результаты "Диалог"'


class ExerciseIrregularEnglishVerbResult(models.Model):
    exercise = models.ForeignKey(
        ExerciseIrregularEnglishVerb,
        on_delete=models.CASCADE,
        related_name='result',
        null=True,
        blank=True
    )
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)

    def set_value(self, step_num, value):
        try:
            self.__dict__[step_num] = value
        except KeyError as err:
            logger.error(err)

    def get_student(self):
        return self.exercise.student if self.exercise else 'Unknown'

    def get_teacher(self):
        return self.exercise.teacher if self.exercise else 'Unknown'

    def get_ex_name(self):
        return self.exercise.name if self.exercise else 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат "Неправильные глаголы"'
        verbose_name_plural = 'Результаты "Неправильные глаголы"'
