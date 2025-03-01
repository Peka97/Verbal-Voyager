from django.db import models
from django.core.exceptions import ValidationError


class AbstractWord(models.Model):
    word = models.CharField(
        verbose_name='Слово в оригинале',
        max_length=50,  # 100
        null=True,
        blank=True,
    )
    translation = models.CharField(
        verbose_name='Перевод на русский',
        max_length=100,  # 255
        null=True,
        blank=True,
    )
    examples = models.TextField(
        verbose_name='Примеры употребления',
        max_length=500,
        null=True,
        blank=True,
        help_text='Напишите одно и или несколько предложений, разделяя их переносом строки.'
    )
    another_means = models.CharField(
        verbose_name='Другие значения',
        max_length=400,  # 500
        blank=True,
        null=True,
        editable=False
    )
    sound_url = models.URLField(
        verbose_name='Аудио файл',
        max_length=300,
        blank=True,
        null=True,
        help_text='Ссылка на аудиофайл с переводом слова.'
    )
    image_url = models.URLField(
        verbose_name='Изображение',
        max_length=150,  # 300
        blank=True,
        null=True,
        help_text='Ссылка на изображение слова.'
    )

    def clean(self):
        if self.word:
            self.word = self.word.lower()
        if self.translation:
            self.translation = self.translation.lower()

    def save(self, *args, **kwargs):
        self.clean()

        super(AbstractWord, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

        indexes = [models.Index(fields=['word',]), ]
        ordering = ['word']


class EnglishWord(AbstractWord):
    SPEECH_CODES = {
        'n': 'noun',
        'v': 'verb',
        'j': 'adjective',
        'r': 'adverb',
        'prp': 'preposition',
        'prn': 'pronoun',
        'crd': 'cardinal number',
        'cjc': 'conjunction',
        'exc': 'interjection',
        'det': 'article',
        'abb': 'abbreviation',
        'x': 'particle',
        'ord': 'ordinal number',
        'md ': 'modal verb',
        'ph ': 'phrase',
        'phi': 'idiom'
    }
    speech_code = models.CharField(
        verbose_name='Код части речи',
        max_length=50,
        choices=SPEECH_CODES,
        blank=True,
        null=True,
        help_text='Код части речи слова в соответствии с Oxford Dictionaries.'
    )
    definition = models.CharField(
        verbose_name='Определение',
        max_length=350,  # 1000
        blank=True,
        null=True,
        help_text='Определение слова'
    )
    prefix = models.CharField(
        verbose_name='Префикс',
        max_length=25,
        blank=True,
        null=True,
        help_text='Префикс'
    )
    transcription = models.CharField(
        verbose_name='Транскрипция',
        max_length=75,  # 100
        blank=True,
        null=True,
        help_text='Транскрипция слова'
    )

    def clean(self):
        super().clean()
        existing_word = EnglishWord.objects.filter(
            word=self.word,
            translation=self.translation
        ).exclude(pk=self.pk)
        if existing_word.exists():
            raise ValidationError(
                f"Такое сочетание слова и перевода уже существует - {existing_word}")

    def save(self, *args, **kwargs):
        self.clean()

        another_means_words = EnglishWord.objects.filter(
            word=self.word).exclude(pk=self.pk).all()
        self.another_means = ', '.join(
            [word.translation for word in another_means_words if word.translation])

        super(EnglishWord, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.word} ({self.speech_code}) - {self.translation}'

    class Meta(AbstractWord.Meta):
        verbose_name = f'{AbstractWord.Meta.verbose_name} | Eng'
        verbose_name_plural = f'{AbstractWord.Meta.verbose_name_plural} | Eng'


class FrenchWord(AbstractWord):
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

    def clean(self):
        existing_word = FrenchWord.objects.filter(
            word=self.word,
            translation=self.translation
        ).exclude(pk=self.pk)
        if existing_word.exists():
            raise ValidationError(
                f"Такое сочетание слова и перевода уже существует - {existing_word}")

    def __str__(self) -> str:
        return f'{self.word} ({self.genus}) - {self.translation}'

    class Meta(AbstractWord.Meta):
        verbose_name = f'{AbstractWord.Meta.verbose_name} | Fr'
        verbose_name_plural = f'{AbstractWord.Meta.verbose_name_plural} | Fr'


class IrregularEnglishVerb(models.Model):
    infinitive = models.ForeignKey(
        verbose_name='Инфинитив',
        to=EnglishWord,
        on_delete=models.SET_NULL,
        related_name='irregular_verb',
        blank=True,
        null=True,
    )
    past_simple = models.CharField(
        verbose_name='Прошедшее время',
        max_length=50,
    )
    past_participle = models.CharField(
        verbose_name='Причастие прошедшего времени',
        max_length=50,
    )

    def __str__(self) -> str:
        return f'{self.infinitive.word if self.infinitive else self.infinitive} - {self.past_simple} - {self.past_participle}'

    class Meta:
        verbose_name = 'Неправильный глагол | Eng'
        verbose_name_plural = 'Неправильные глаголы | Eng'

        ordering = ['infinitive__word']
