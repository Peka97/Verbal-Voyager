from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError


User = get_user_model()


class Word(models.Model):
    word = models.CharField(
        verbose_name='Слово в оригинале',
        max_length=50
        )
    translate = models.CharField(
        verbose_name='Перевод на русский',
        max_length=255
        )
    lang = models.CharField(
        verbose_name='Язык оригинала',
        max_length=10,
        default='eng',
        choices=[
            ('eng', 'English'),
            ('fr', 'French'),
            ('sp', 'Spanish')
        ]
    )
    sentences = models.TextField(
        verbose_name='Примеры употребления',
        max_length=500, 
        null=True, 
        blank=True,
        help_text='Напишите одно и или несколько предложений, разделяя их переносом строки.'
        )

    def __str__(self) -> str:
        return f'{self.lang} | {self.word} ({self.translate})'

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        ordering = ['word']


class ExerciseWords(models.Model):
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения',
                            help_text="Поле заполняется автоматически, если остаётся пустым")
    words = models.ManyToManyField(Word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='words_student', 
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, 
        verbose_name='Ученик'
        )
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='words_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель"
        )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def get_words(self):
        words = [
            f'{word.word} - {word.translate}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'
    
    def get_absolute_url(self):
        return reverse("exercises_words", kwargs={"ex_id": self.pk, "step": 1})
    
    def get_url(self):
        return 'https://verbal-voyager.ru' + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'
    

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = ExerciseWords.objects.filter(student=self.student).count()
            self.name = f"Words {student_exercises_count + 1}"
        super(ExerciseWords, self).save(*args, **kwargs)

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Слова"'
        verbose_name_plural = 'Упражнения "Слова"'
        ordering = ['-is_active']


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
        User, on_delete=models.CASCADE, 
        related_name='dialog_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dialog_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = ExerciseDialog.objects.filter(student=self.student).count()
            self.name = f"Dialog {student_exercises_count + 1}"
        super(ExerciseDialog, self).save(*args, **kwargs)
        
    def get_words(self):
        words = [
            f'{word.word} - {word.translate}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))
    
    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'
    
    def get_absolute_url(self):
        return reverse("exercises_dialog", kwargs={"ex_id": self.pk})
    
    def get_url(self):
        return 'https://verbal-voyager.ru' + self.get_absolute_url()

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Диалог"'
        verbose_name_plural = 'Упражнения "Диалог"'
        ordering = ['-is_active']

class ExerciseWordsResult(models.Model):
    words = models.ForeignKey(
        ExerciseWords, on_delete=models.CASCADE, related_name='words_result', null=True, blank=True)
    step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
    step_4 = models.SmallIntegerField(null=True, blank=True, default=None)
    
    def get_student(self):
        if self.words:
            return self.words.student
        return 'Unknown'

    def get_teacher(self):
        if self.words:
            return self.words.teacher
        return 'Unknown'

    def get_ex_name(self):
        if self.words:
            return self.words.name
        return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат упражнения "Слова"'
        verbose_name_plural = 'Результаты упражнений "Слова"'
    
class ExerciseDialogResult(models.Model):
    dialog = models.ForeignKey(
        ExerciseDialog, on_delete=models.CASCADE, related_name='dialog_result', null=True, blank=True)
    points = models.SmallIntegerField()
    
    def get_student(self):
        if self.dialog:
            return self.dialog.student
        return 'Unknown'

    def get_teacher(self):
        if self.dialog:
            return self.dialog.teacher
        return 'Unknown'

    def get_ex_name(self):
        if self.dialog:
            return self.dialog.name
        return 'Unknown'

    get_student.short_description = 'Студент'
    get_teacher.short_description = 'Учитель'
    get_ex_name.short_description = 'Название'

    class Meta:
        verbose_name = 'Результат упражнения "Диалог"'
        verbose_name_plural = 'Результаты упражнений "Диалог"'
