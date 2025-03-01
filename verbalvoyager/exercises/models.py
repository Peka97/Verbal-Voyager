from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError

from verbalvoyager.settings import SITE_NAME
from dictionary.models import EnglishWord as new_eng_word, FrenchWord as new_fr_word, IrregularEnglishVerb


User = get_user_model()


class Word(models.Model):  # TODO: delete after update
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


class EnglishWord(models.Model):  # TODO: delete after update
    word = models.CharField(
        verbose_name='Слово в оригинале',
        max_length=50
    )
    translate = models.CharField(
        verbose_name='Перевод на русский',
        max_length=255
    )
    sentences = models.TextField(
        verbose_name='Примеры употребления',
        max_length=500,
        null=True,
        blank=True,
        help_text='Напишите одно и или несколько предложений, разделяя их переносом строки.'
    )

    def __str__(self) -> str:
        return f'{self.word} - {self.translate}'

    class Meta:
        verbose_name = 'Слово (eng) (old)'
        verbose_name_plural = 'Слова (eng) (old)'
        ordering = ['word']


class FrenchWord(models.Model):  # TODO: delete after update
    word = models.CharField(
        verbose_name='Слово в оригинале',
        max_length=50
    )
    genus = models.CharField(
        verbose_name='Род слова',
        max_length=50,
        choices=[
            ('m', 'Мужской'),
            ('f', 'Женский'),
            ('n', 'Средний')
        ],
        blank=True,
        null=True
    )
    translate = models.CharField(
        verbose_name='Перевод на русский',
        max_length=255
    )

    sentences = models.TextField(
        verbose_name='Примеры употребления',
        max_length=500,
        null=True,
        blank=True,
        help_text='Напишите одно и или несколько предложений, разделяя их переносом строки.'
    )

    def __str__(self) -> str:
        return f'{self.word} ({self.genus}) - {self.translate}'

    class Meta:
        verbose_name = 'Слово (french) (old)'
        verbose_name_plural = 'Слова (french) (old)'
        ordering = ['word']


class ExerciseWords(models.Model):  # TODO: delete after update
    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения',
                            help_text="Поле заполняется автоматически, если остаётся пустым")
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
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
        return SITE_NAME + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = ExerciseWords.objects.filter(
                student=self.student).count()
            self.name = f"Words {student_exercises_count + 1}"
        super(ExerciseWords, self).save(*args, **kwargs)

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Слова" (old)'
        verbose_name_plural = 'Упражнения "Слова" (old)'
        ordering = ['-is_active']


# ExerciseWords
class AbstractExerciseWords(models.Model):
    view_name = 'exercise_words'

    name = models.CharField(
        default=None, blank=True, max_length=50,
        verbose_name='Название упражнения',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def get_words(self):
        words = [
            f'{word.word} - {word.translation}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'

    def get_url(self):
        return SITE_NAME + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.objects.filter(
                student=obj.student).count()
            self.name = f"Words {student_exercises_count + 1}"

        super().save_model(request, obj, form, change)

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        abstract = True
        ordering = ['-is_active']


class ExerciseEnglishWords(AbstractExerciseWords):

    words = models.ManyToManyField(new_eng_word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_eng_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_eng_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель"
    )

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "english", "ex_id": self.pk, "step": 1})

    def __str__(self):
        return f"{self.name} (ENG)"

    class Meta:
        verbose_name = 'Eng | Words'
        verbose_name_plural = 'Eng | Words'


class ExerciseFrenchWords(AbstractExerciseWords):
    words = models.ManyToManyField(new_fr_word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_fr_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_fr_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель"
    )

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "french", "ex_id": self.pk, "step": 1})

    def __str__(self):
        return f"{self.name} (FR)"

    class Meta:
        verbose_name = 'Fr | Words'
        verbose_name_plural = 'Fr | Words'


class ExerciseDialog(models.Model):  # TODO: delete after update
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
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='dialog_student_old',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dialog_teacher_old',
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
            student_exercises_count = ExerciseDialog.objects.filter(
                student=self.student).count()
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
        return SITE_NAME + self.get_absolute_url()

    def __str__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        verbose_name = 'Упражнение "Диалог" (old)'
        verbose_name_plural = 'Упражнения "Диалог" (old)'
        ordering = ['-is_active']


# ExerciseDialog
class AbstractExerciseDialog(models.Model):
    view_name = 'exercise_dialog'

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
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def save(self, *args, **kwargs):
        if not self.name:
            try:
                student_exercises_count = self.objects.filter(
                    student=self.student).count()
            except AttributeError:
                self.name = "Dialog 1"
            else:
                self.name = f"Dialog {student_exercises_count + 1}"
        super().save(*args, **kwargs)

    def get_words(self):
        words = [
            f'{word.word} - {word.translation}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'

    def get_url(self):
        return SITE_NAME + self.get_absolute_url()

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        abstract = True
        ordering = ['-is_active']


class ExerciseEnglishDialog(AbstractExerciseDialog):
    words = models.ManyToManyField(new_eng_word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_eng_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_eng_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель")

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "english", "ex_id": self.pk})

    def __str__(self) -> str:
        return f"{self.name} (ENG)"

    class Meta:
        verbose_name = 'Eng | Dialog'
        verbose_name_plural = 'Eng | Dialog'


class ExerciseFrenchDialog(AbstractExerciseDialog):
    words = models.ManyToManyField(new_fr_word, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_fr_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_fr_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель")

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "french", "ex_id": self.pk})

    def __str__(self) -> str:
        return f"{self.name} (FR)"

    class Meta:
        verbose_name = 'Fr | Dialog'
        verbose_name_plural = 'Fr | Dialog'


class ExerciseWordsResult(models.Model):  # TODO: delete after update
    words = models.ForeignKey(
        ExerciseWords, on_delete=models.CASCADE, related_name='words_result_old', null=True, blank=True)
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
        verbose_name = 'Результат упражнения "Слова" (old)'
        verbose_name_plural = 'Результаты упражнений "Слова" (old)'

# class ExerciseEnglishWordsResult(models.Model):
#     words = models.ForeignKey(
#         ExerciseEnglishWords, on_delete=models.CASCADE, related_name='words_eng_result', null=True, blank=True)
#     step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_4 = models.SmallIntegerField(null=True, blank=True, default=None)

#     def get_student(self):
#         if self.words:
#             return self.words.student
#         return 'Unknown'

#     def get_teacher(self):
#         if self.words:
#             return self.words.teacher
#         return 'Unknown'

#     def get_ex_name(self):
#         if self.words:
#             return self.words.name
#         return 'Unknown'

#     get_student.short_description = 'Студент'
#     get_teacher.short_description = 'Учитель'
#     get_ex_name.short_description = 'Название'

#     class Meta:
#         verbose_name = 'Результат упражнения "Слова" (eng)'
#         verbose_name_plural = 'Результаты упражнений "Слова" (eng)'

# class ExerciseFrenchWordsResult(models.Model):
#     words = models.ForeignKey(
#         ExerciseFrenchWords, on_delete=models.CASCADE, related_name='words_fr_result', null=True, blank=True)
#     step_1 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_2 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_3 = models.SmallIntegerField(null=True, blank=True, default=None)
#     step_4 = models.SmallIntegerField(null=True, blank=True, default=None)

#     def get_student(self):
#         if self.words:
#             return self.words.student
#         return 'Unknown'

#     def get_teacher(self):
#         if self.words:
#             return self.words.teacher
#         return 'Unknown'

#     def get_ex_name(self):
#         if self.words:
#             return self.words.name
#         return 'Unknown'

#     get_student.short_description = 'Студент'
#     get_teacher.short_description = 'Учитель'
#     get_ex_name.short_description = 'Название'

#     class Meta:
#         verbose_name = 'Результат упражнения "Слова" (fr)'
#         verbose_name_plural = 'Результаты упражнений "Слова" (fr)'


class ExerciseDialogResult(models.Model):  # TODO: delete after update
    dialog = models.ForeignKey(
        ExerciseDialog, on_delete=models.CASCADE, related_name='dialog_result_old', null=True, blank=True)
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
        verbose_name = 'Результат упражнений "Диалог" (old)'
        verbose_name_plural = 'Результаты упражнений "Диалог" (old)'


# Irregular Verb
class ExerciseIrregularEnglishVerb(models.Model):
    view_name = 'exercise_irregular_verbs'

    name = models.CharField(
        default=None, blank=True, max_length=50,
        verbose_name='Название упражнения',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    words = models.ManyToManyField(IrregularEnglishVerb, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='irregular_verbs_student',
        limit_choices_to={'groups__name__in': ['Student', ]},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='irregular_verbs_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', ]},
        null=True,
        verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def get_words(self):
        words = [
            word.infinitive.word for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_id": self.pk, "step": '1'})

    def get_url(self):
        return SITE_NAME + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.objects.filter(
                student=obj.student).count()
            self.name = f"Irregular Verbs {student_exercises_count + 1}"

        super().save_model(request, obj, form, change)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        verbose_name = verbose_name_plural = 'Eng | Irregular Verb '
        ordering = ['-is_active']
