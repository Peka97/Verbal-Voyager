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
        verbose_name = 'База слов'
        verbose_name_plural = 'База слов'


class ExerciseWords(models.Model):
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения',
                            help_text="Поле заполняется автоматически, если остаётся пустым")
    words = models.ManyToManyField(Word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='words_student', null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='words_teacher', null=True, verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def get_words(self):
        words = [
            f'{word.word} - {word.translate}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Упражнение "Слова"'

    # def get_teachers(self):
    #     teachers = [user for user in User.objects.all() if user.groups.filter(name='Teacher').exists()]
    #     return ' '.join(teachers)

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = len(
                list(ExerciseWords.objects.filter(student=self.student).all()))
            self.name = f"Words {student_exercises_count + 1}"
        super(ExerciseWords, self).save(*args, **kwargs)

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Слова"'
        verbose_name_plural = 'Упражнения "Слова"'


class ExerciseDialog(models.Model):
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения',
                            help_text="Поле заполняется автоматически, если остаётся пустым")
    text = models.TextField(blank=False, null=True, verbose_name='Текст',
                            help_text="""
                            Требуемый формат:
                            Scene: *some text*
                            Person: *some text*
                            Another person: *some text*
                            ...
                            """)
    words = models.ManyToManyField(Word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='dialog_student',
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='dialog_teacher',
        null=True, verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = len(
                list(ExerciseDialog.objects.filter(student=self.student).all()))
            self.name = f"Dialog {student_exercises_count + 1}"
        super(ExerciseDialog, self).save(*args, **kwargs)

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Диалог"'
        verbose_name_plural = 'Упражнения "Диалог"'


class ExerciseResult(models.Model):
    words = models.ForeignKey(
        ExerciseWords, on_delete=models.CASCADE, related_name='words_result', null=True, blank=True)
    dialog = models.ForeignKey(
        ExerciseDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_4 = models.SmallIntegerField(null=True, blank=True, default=None)

    def __str__(self) -> str:
        if self.words:
            return self.words.name
        elif self.dialog:
            return self.dialog.name
        else:
            return 'Unknown'

    def get_student(self):
        if self.words:
            return self.words.student
        elif self.dialog:
            return self.dialog.student
        else:
            return 'Unknown'

    def get_teacher(self):
        if self.words:
            return self.words.teacher
        elif self.dialog:
            return self.dialog.teacher
        else:
            return 'Unknown'

    def get_ex_name(self):
        if self.words:
            return self.words.name
        elif self.dialog:
            return self.dialog.name
        else:
            return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат упражнения'
        verbose_name_plural = 'Результаты упражнений'
