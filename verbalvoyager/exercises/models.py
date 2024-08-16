from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html
from django.core.exceptions import ValidationError


User = get_user_model()


class Word(models.Model):
    word = models.CharField(max_length=50)
    translate = models.CharField(max_length=255)
    lang = models.CharField(
        max_length=10,
        default='eng',
        choices=[
            ('eng', 'English'),
            ('fr', 'French'),
            ('sp', 'Spanish')
        ]
    )
    sentences = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.lang} | {self.word} ({self.translate})'

    class Meta:
        verbose_name = 'Слово для изучения'
        verbose_name_plural = 'Слова для изучения'


class Exercise(models.Model):
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения')
    words = models.ManyToManyField(Word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='exer_student', null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='exer_teacher', null=True, verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def get_words(self):
        words = [
            f'{word.word} - {word.translate}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова'

    # def get_teachers(self):
    #     teachers = [user for user in User.objects.all() if user.groups.filter(name='Teacher').exists()]
    #     return ' '.join(teachers)

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = len(
                list(Exercise.objects.filter(student=self.student).all()))
            self.name = f"Exercise {student_exercises_count + 1}"
        super(Exercise, self).save(*args, **kwargs)

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.id} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        verbose_name = 'Упражнение'
        verbose_name_plural = 'Упражнения'


class ExerciseResult(models.Model):
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name='exercise_result', null=True)
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_4 = models.SmallIntegerField(null=True, blank=True, default=None)

    def __str__(self) -> str:
        return self.exercise.name

    def get_student(self):
        return self.exercise.student

    def get_teacher(self):
        return self.exercise.teacher

    def get_ex_name(self):
        return self.exercise.name

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат упражнения'
        verbose_name_plural = 'Результаты упражнений'


class Dialog(models.Model):
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения')
    text = models.TextField(blank=False, null=True, verbose_name='Текст')
    words = models.ManyToManyField(Word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='dialog_student',
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='dialog_teacher',
        null=True, verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'
