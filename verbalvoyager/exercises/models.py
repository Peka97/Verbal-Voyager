from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings
from dictionary.models import EnglishWord, FrenchWord, IrregularEnglishVerb, SpanishWord


User = get_user_model()


class ExerciseCategory(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Категория упражнений',
        help_text='Категория, в которую будут помещены упражнения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория упражнений'
        verbose_name_plural = 'Категории упражнений'
        ordering = ['name',]
# ExerciseWords


class AbstractExerciseWords(models.Model):
    view_name = 'exercise_words'

    name = models.CharField(
        default=None,
        blank=True,
        null=True,
        max_length=50,
        verbose_name='Название упражнения',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    category = models.ForeignKey(
        ExerciseCategory,
        verbose_name='Категория упражнения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Категория, связывающая упражнение с чем-либо, например, учебник, книга или фильм'
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
        return settings.SITE_NAME + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'

    def save(self, *args, **kwargs):
        if not self.name:
            student_exercises_count = self.__class__.objects.filter(
                student=self.student).count()
            self.name = f"Words {student_exercises_count + 1}"

        return super().save(*args, **kwargs)

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        abstract = True
        ordering = ['-is_active']


class ExerciseEnglishWords(AbstractExerciseWords):
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_eng_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_eng_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
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
    words = models.ManyToManyField(FrenchWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_fr_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_fr_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
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
        

class ExerciseRussianWords(AbstractExerciseWords):
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_ru_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_ru_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель"
    )

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "russian", "ex_id": self.pk, "step": 1})

    def __str__(self):
        return f"{self.name} (RU)"

    class Meta:
        verbose_name = 'Ru | Words'
        verbose_name_plural = 'Ru | Words'

class ExerciseSpanishWords(AbstractExerciseWords):
    words = models.ManyToManyField(SpanishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_sp_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True,
        verbose_name='Ученик'
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='words_sp_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель"
    )

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "spanish", "ex_id": self.pk, "step": 1})

    def __str__(self):
        return f"{self.name} (SP)"

    class Meta:
        verbose_name = 'Sp | Words'
        verbose_name_plural = 'Sp | Words'

# ExerciseDialog
class AbstractExerciseDialog(models.Model):
    view_name = 'exercise_dialog'

    name = models.CharField(default=None, blank=True, max_length=50,
                            verbose_name='Название упражнения',
                            help_text="Поле заполняется автоматически, если остаётся пустым")
    category = models.ForeignKey(
        ExerciseCategory,
        verbose_name='Категория упражнения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Категория, связывающая упражнение с чем-либо, например, учебник, книга или фильм'
    )
    text = models.TextField(blank=False, null=True, verbose_name='Текст',
                            help_text="""
                            Требуемый формат:
                            Scene: text
                            Person Name: text
                            Another Person Name: text
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
        return super().save(*args, **kwargs)

    def get_words(self):
        words = [
            f'{word.word} - {word.translation}<br>' for word in self.words.all()
        ]
        return format_html(' '.join(words))

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'

    def get_url(self):
        return settings.SITE_NAME + self.get_absolute_url()

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student.last_name} {self.student.first_name} - {status}"

    class Meta:
        abstract = True
        ordering = ['-is_active']


class ExerciseEnglishDialog(AbstractExerciseDialog):
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_eng_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_eng_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
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
    words = models.ManyToManyField(FrenchWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_fr_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_fr_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель")

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "french", "ex_id": self.pk})

    def __str__(self) -> str:
        return f"{self.name} (FR)"

    class Meta:
        verbose_name = 'Fr | Dialog'
        verbose_name_plural = 'Fr | Dialog'

class ExerciseRussianDialog(AbstractExerciseDialog):
    words = models.ManyToManyField(EnglishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_ru_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_ru_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель")

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "russian", "ex_id": self.pk})

    def __str__(self) -> str:
        return f"{self.name} (RU)"

    class Meta:
        verbose_name = 'Ru | Dialog'
        verbose_name_plural = 'Ru | Dialog'


class ExerciseSpanishDialog(AbstractExerciseDialog):
    words = models.ManyToManyField(SpanishWord, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='dialog_sp_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='dialog_sp_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель")

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_lang": "spanish", "ex_id": self.pk})

    def __str__(self) -> str:
        return f"{self.name} (SP)"

    class Meta:
        verbose_name = 'Sp | Dialog'
        verbose_name_plural = 'Sp | Dialog'


# Irregular Verb
class ExerciseIrregularEnglishVerb(models.Model):
    view_name = 'exercise_irregular_verbs'

    name = models.CharField(
        default=None, blank=True, max_length=50,
        verbose_name='Название упражнения',
        help_text="Поле заполняется автоматически, если остаётся пустым"
    )
    category = models.ForeignKey(
        ExerciseCategory,
        verbose_name='Категория упражнения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Категория, связывающая упражнение с чем-либо, например, учебник, книга или фильм'
    )
    words = models.ManyToManyField(IrregularEnglishVerb, verbose_name="Слова")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='irregular_verbs_student',
        limit_choices_to={'groups__name__in': ['Student', 'StudentDemo']},
        null=True, verbose_name='Ученик')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='irregular_verbs_teacher',
        limit_choices_to={'groups__name__in': ['Teacher', 'TeacherDemo']},
        null=True,
        verbose_name="Учитель")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    external_access = models.BooleanField(
        verbose_name='Внешний доступ к упражнению',
        default=False,
        help_text='Если установлено, любой может получить доступ к упражнению без регистрации или авторизации',
    )

    def get_words(self):
        try:
            words = [
                word.infinitive.word for word in self.words.select_related('infinitive').all()
            ]
            return format_html(', '.join(words))
        except AttributeError:
            return 'В одном или нескольких словах не выбран инфинитив. Вывод слов невозможен.'

    get_words.allow_tags = True
    get_words.short_description = 'Слова в упражнении'

    def get_absolute_url(self):
        return reverse(self.view_name, kwargs={"ex_id": self.pk, "step": '1'})

    def get_url(self):
        return settings.SITE_NAME + self.get_absolute_url()
    get_words.get_url = 'Ссылка на упражнение'

    def save_model(self, request, obj, form, change):
        if not obj.name:
            student_exercises_count = self.objects.filter(
                student=obj.student).count()
            self.name = f"Irregular Verbs {student_exercises_count + 1}"

        return super().save_model(request, obj, form, change)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        status = 'Active' if self.is_active else 'Done'
        return f"{self.pk} - {self.student} - {status}"

    class Meta:
        verbose_name = verbose_name_plural = 'Eng | Irregular Verb '
        ordering = ['-is_active']
