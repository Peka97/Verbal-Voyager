import logging

from django.db import models

from exercises.models import ExerciseWords, ExerciseDialog, NewExerciseIrregularEnglishVerb

logger = logging.getLogger('django')

# ExerciseWordsResult

# class AnstractExerciseWordsResult(models.Model):
#     step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_4 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_5 = models.SmallIntegerField(null=True, blank=True, default=None)

#     def set_value(self, step_num, value):
#         try:
#             self.__dict__[step_num] = value

#             if step_num[-1] == '5':
#                 self.exercise.is_active = False
#         except KeyError as err:
#             logger.error(err)

#     def get_student(self):
#         if self.exercise:
#             return self.exercise.student
#         return 'Unknown'

#     def get_teacher(self):
#         if self.exercise:
#             return self.exercise.teacher
#         return 'Unknown'

#     def get_ex_name(self):
#         if self.exercise:
#             return self.exercise.name
#         return 'Unknown'

#     get_student.short_description = 'Студент'
#     get_teacher.short_description = 'Учитель'
#     get_ex_name.short_description = 'Название'

#     class Meta:
#         abstract = True


# class ExerciseEnglishWordsResult(AnstractExerciseWordsResult):
#     exercise = models.ForeignKey(
#         ExerciseEnglishWords, on_delete=models.CASCADE, related_name='words_eng_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Eng | Результат "Слова"'
#         verbose_name_plural = 'Eng | Результаты "Слова"'


# class ExerciseFrenchWordsResult(AnstractExerciseWordsResult):
#     exercise = models.ForeignKey(
#         ExerciseFrenchWords, on_delete=models.CASCADE, related_name='words_fr_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Fr | Результат "Слова"'
#         verbose_name_plural = 'Fr | Результаты "Слова"'


# class ExerciseRussianWordsResult(AnstractExerciseWordsResult):
#     exercise = models.ForeignKey(
#         ExerciseRussianWords, on_delete=models.CASCADE, related_name='words_ru_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Ru | Результат "Слова"'
#         verbose_name_plural = 'Ru | Результаты "Слова"'


# class ExerciseSpanishWordsResult(AnstractExerciseWordsResult):
#     exercise = models.ForeignKey(
#         ExerciseSpanishWords, on_delete=models.CASCADE, related_name='words_sp_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Sp | Результат "Слова"'
#         verbose_name_plural = 'Sp | Результаты "Слова"'


# # ExerciseDialogResult
# class AbstractExerciseDialogResult(models.Model):
#     points = models.SmallIntegerField(null=True, blank=True)

#     def set_value(self, step_num, value):
#         self.points = value

#     def get_student(self):
#         if self.exercise:
#             return self.exercise.student
#         return 'Unknown'

#     def get_teacher(self):
#         if self.exercise:
#             return self.exercise.teacher
#         return 'Unknown'

#     def get_ex_name(self):
#         if self.exercise:
#             return self.exercise.name
#         return 'Unknown'

#     get_student.short_description = 'Студент'
#     get_teacher.short_description = 'Учитель'
#     get_ex_name.short_description = 'Название'

#     class Meta:
#         abstract = True


# class ExerciseEnglishDialogResult(AbstractExerciseDialogResult):
#     exercise = models.ForeignKey(
#         ExerciseEnglishDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Eng | Результат "Диалог"'
#         verbose_name_plural = 'Eng | Результаты "Диалог"'


# class ExerciseFrenchDialogResult(AbstractExerciseDialogResult):
#     exercise = models.ForeignKey(
#         ExerciseFrenchDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Fr | Результат "Диалог"'
#         verbose_name_plural = 'Fr | Результаты "Диалог"'


# class ExerciseSpanishDialogResult(AbstractExerciseDialogResult):
#     exercise = models.ForeignKey(
#         ExerciseSpanishDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Sp | Результат "Диалог"'
#         verbose_name_plural = 'Sp | Результаты "Диалог"'


# class ExerciseRussianDialogResult(AbstractExerciseDialogResult):
#     exercise = models.ForeignKey(
#         ExerciseRussianDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

#     class Meta:
#         verbose_name = 'Ru | Результат "Диалог"'
#         verbose_name_plural = 'Ru | Результаты "Диалог"'

# # ExerciseIrregularEnglishVerb


# class ExerciseIrregularEnglishVerbResult(models.Model):
#     exercise = models.ForeignKey(
#         ExerciseIrregularEnglishVerb, on_delete=models.CASCADE, related_name='irregular_verbs_result', null=True, blank=True
#     )
#     step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_3 = models.SmallIntegerField(null=True, blank=True, default=None)

#     def set_value(self, step_num, value):
#         try:
#             self.__dict__[step_num] = value

#             if step_num[-1] == '3':
#                 self.exercise.is_active = False
#         except KeyError as err:
#             logger.error(err)

#     def get_student(self):
#         if self.exercise:
#             return self.exercise.student
#         return 'Unknown'

#     def get_teacher(self):
#         if self.exercise:
#             return self.exercise.teacher
#         return 'Unknown'

#     def get_ex_name(self):
#         if self.exercise:
#             return self.exercise.name
#         return 'Unknown'

#     get_student.short_description = 'Студент'
#     get_teacher.short_description = 'Учитель'
#     get_ex_name.short_description = 'Название'

#     class Meta:
#         verbose_name = 'Eng | Результат "Неправильные глаголы"'
#         verbose_name_plural = 'Eng | Результаты "Неправильные глаголы"'


# New models
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


class NewExerciseIrregularEnglishVerbResult(models.Model):
    exercise = models.ForeignKey(
        NewExerciseIrregularEnglishVerb,
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
