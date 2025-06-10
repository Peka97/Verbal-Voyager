from django.db import models


class EnglishLessonPlan(models.Model):
    lesson_id = models.ForeignKey(
        'event_calendar.Lesson',
        verbose_name='Урок',
        on_delete=models.SET_NULL,
        related_name='lesson_plan',
        blank=True,
        null=True,
        help_text="Урок, к которому составлен план"
    )
    exercise_id = models.ForeignKey(
        'exercises.ExerciseEnglishWords',
        verbose_name='Упражнение',
        on_delete=models.SET_NULL,
        related_name='english_lesson_plan',
        blank=True,
        null=True,
        help_text='Упражнение с новыми словами (генерируется автоматически)'
    )
    theme = models.CharField(
        verbose_name='Тема',
        max_length=100,
        blank=True,
        null=True,
        help_text="Опиши основные темы урока"
    )
    new_vocabulary = models.ManyToManyField(
        'dictionary.EnglishWord',
        verbose_name='Новые слова',
        related_name='new_vocabulary',
        blank=True,
        help_text="Новые слова"
    )
    processes = models.TextField(
        verbose_name='Процессы',
        max_length=250,
        blank=True,
        null=True,
        help_text="Ссылки на сторонние ресурсы"
    )
    materials = models.CharField(
        max_length=250,
        verbose_name='Материалы',
        blank=True,
        null=True,
        help_text="Пройденные страницы"
    )
    # TODO: Добавить поле с файлами

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     words = self.new_vocabulary
    #     print(words)
    #     print(self.exercise_id)

    #     if not self.exercise_id and words.exists():

    #         new_exercise = ExerciseEnglishWords.objects.create(
    #             name=None,
    #             student=self.lesson_id.student_id,
    #             teacher=self.lesson_id.teacher_id,
    #             is_active=True,
    #         )
    #         new_exercise.save()
    #         new_exercise.words.set(words.all())
    #         self.exercise_id = new_exercise
    #         self.save()

    def __str__(self):
        if self.theme:
            return f"{self.theme} [{self.pk}]"
        else:
            return f"LessonPlan for Lesson_{self.lesson_id}[{self.pk}]"

    class Meta:
        verbose_name = 'План урока'
        verbose_name_plural = 'Планы уроков'


class EnglishLessonMainAims(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название цели урока',
        help_text="Опиши цель урока"
    )
    lesson_plan_id = models.ForeignKey(
        'EnglishLessonPlan',
        verbose_name='План урока',
        on_delete=models.SET_NULL,
        related_name='main_aims',
        blank=True,
        null=True,
        help_text="План урока, к которому относится цель"
    )

    def __str__(self):
        return f"{self.name} [{self.pk}]"

    class Meta:
        verbose_name = 'Основные цели урока'
        verbose_name_plural = 'Основные цели урока'


class EnglishLessonSubsidiaryAims(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название цели урока',
        help_text="Опиши цель урока"
    )
    lesson_plan_id = models.ForeignKey(
        'EnglishLessonPlan',
        verbose_name='План урока',
        on_delete=models.SET_NULL,
        related_name='subsidiary_aims',
        blank=True,
        null=True,
        help_text="План урока, к которому относится цель"
    )

    def __str__(self):
        return f"{self.name} [{self.pk}]"

    class Meta:
        verbose_name = 'Подзадачи урока'
        verbose_name_plural = 'Подзадачи урока'
