from django.db import models

from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseDialog, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb


# ExerciseWordsResult
class AnstractExerciseWordsResult(models.Model):
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_4 = models.SmallIntegerField(null=True, blank=True, default=None)

    def get_student(self):
        if self.exercise_id:
            return self.exercise_id.student
        return 'Unknown'

    def get_teacher(self):
        if self.exercise_id:
            return self.exercise_id.teacher
        return 'Unknown'

    def get_ex_name(self):
        if self.exercise_id:
            return self.exercise_id.name
        return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        abstract = True


class ExerciseEnglishWordsResult(AnstractExerciseWordsResult):
    exercise_id = models.ForeignKey(
        ExerciseEnglishWords, on_delete=models.CASCADE, related_name='words_eng_result', null=True, blank=True)

    class Meta:
        verbose_name = 'Результат "Слова" | Eng'
        verbose_name_plural = 'Результаты "Слова" | Eng'


class ExerciseFrenchWordsResult(AnstractExerciseWordsResult):
    exercise_id = models.ForeignKey(
        ExerciseFrenchWords, on_delete=models.CASCADE, related_name='words_fr_result', null=True, blank=True)

    class Meta:
        verbose_name = 'Результат "Слова" | Fr'
        verbose_name_plural = 'Результаты "Слова" | Fr'


# ExerciseDialogResult
class AbstractExerciseDialogResult(models.Model):
    points = models.SmallIntegerField(null=True, blank=True)

    def get_student(self):
        if self.exercise_id:
            return self.exercise_id.student
        return 'Unknown'

    def get_teacher(self):
        if self.exercise_id:
            return self.exercise_id.teacher
        return 'Unknown'

    def get_ex_name(self):
        if self.exercise_id:
            return self.exercise_id.name
        return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        abstract = True


class ExerciseEnglishDialogResult(AbstractExerciseDialogResult):
    exercise_id = models.ForeignKey(
        ExerciseEnglishDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

    class Meta:
        verbose_name = 'Результат "Диалог" | Eng'
        verbose_name_plural = 'Результаты "Диалог" | Eng'


class ExerciseFrenchDialogResult(AbstractExerciseDialogResult):
    exercise_id = models.ForeignKey(
        ExerciseFrenchDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)

    class Meta:
        verbose_name = 'Результат "Диалог" | Fr'
        verbose_name_plural = 'Результаты "Диалог" | Fr'


# ExerciseIrregularEnglishVerb
class ExerciseIrregularEnglishVerbResult(models.Model):
    exercise_id = models.ForeignKey(
        ExerciseIrregularEnglishVerb, on_delete=models.CASCADE, related_name='irregular_verbs_result', null=True, blank=True
    )
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)

    def get_student(self):
        if self.exercise_id:
            return self.exercise_id.student
        return 'Unknown'

    def get_teacher(self):
        if self.exercise_id:
            return self.exercise_id.teacher
        return 'Unknown'

    def get_ex_name(self):
        if self.exercise_id:
            return self.exercise_id.name
        return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат "Неправильные глаголы" | Eng'
        verbose_name_plural = 'Результаты "Неправильные глаголы" | Eng'
