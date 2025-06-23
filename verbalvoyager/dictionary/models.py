from django.db import models
from django.db.models import Prefetch
from django.core.exceptions import ValidationError


class Language(models.Model):
    name = models.CharField(
        max_length=10,
        verbose_name='Язык'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'


class WordQuerySet(models.QuerySet):
    def prefetch_details(self, language_name=None):
        if not language_name:
            return self.prefetch_related(
                Prefetch('englishworddetail',
                         queryset=EnglishWordDetail.objects.all(),
                         to_attr='english_detail'),
                Prefetch('frenchworddetail',
                         queryset=FrenchWordDetail.objects.all(),
                         to_attr='french_detail'),
                Prefetch('spanishworddetail',
                         queryset=SpanishWordDetail.objects.all(),
                         to_attr='spanish_detail')
            )

        language_name = language_name.lower()

        match language_name:
            case 'english':
                obj_name = EnglishWordDetail
            case 'french':
                obj_name = FrenchWordDetail
            case 'spanish':
                obj_name = SpanishWordDetail

        return self.prefetch_related(
            Prefetch(f'{language_name.lower()}worddetail',
                     queryset=obj_name.objects.all(),
                     to_attr=f'_{language_name.lower()}_detail')
        )


class WordManager(models.Manager):
    def get_queryset(self):
        return WordQuerySet(self.model, using=self._db)

    def prefetch_details(self, language_name=None):
        return self.get_queryset().prefetch_details(language_name)


class Word(models.Model):
    word = models.CharField(
        max_length=50,
        verbose_name='Слово'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='words',
        verbose_name='Язык'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WordManager()

    @property
    def details(self):
        language_to_detail = {
            'english': '_english_detail',
            'french': '_french_detail',
            'spanish': '_spanish_detail',
        }

        lang_code = self.language.name.lower()
        detail_attr = language_to_detail.get(lang_code)

        if not detail_attr:
            return None

        details = getattr(self, detail_attr, None)
        return details

    def __str__(self):
        return f"{self.word} [{self.language}]"

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        unique_together = ('language', 'word')
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['language', 'word']),
        ]
        ordering = ['word']


class Translation(models.Model):
    SPEECH_CODES = {
        '': 'none',
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

    source_word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='translations_from',
        verbose_name='Слово-источник',
        help_text='Слово, которое переводится.'
    )
    target_word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='translations_to',
        verbose_name='Слово-цель',
        help_text='Слово, на которое переводится.'
    )
    part_of_speech = models.CharField(
        max_length=20,
        choices=SPEECH_CODES,
        blank=True,
        default='',
        verbose_name='Часть речи',
        help_text='Часть речи слова-источника в данном переводе.'
    )
    definition = models.TextField(
        blank=True,
        default='',
        verbose_name='Определение',
        help_text='Определение слова-источника в данном переводе.'
    )
    examples = models.JSONField(
        blank=True,
        default=dict,
        verbose_name='Примеры',
        help_text='Примеры использования слова-источника в данном переводе.'
    )
    prefix = models.CharField(
        max_length=10,
        blank=True,
        default='',
        verbose_name='Префикс',
        help_text='Префикс слова-источника в данном переводе.'
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Ссылка на изображение слова.'
    )

    def save(self, *args, **kwargs):
        if self.source_word.language == self.target_word.language:
            raise ValidationError(
                'Слово-источник и слово-цель должны быть на разных языках.')
        if self.source_word == self.target_word:
            raise ValidationError(
                'Слово-источник и слово-цель должны быть разными.')
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'
        constraints = [
            models.UniqueConstraint(
                name='unique_translation_composite',
                fields=['source_word', 'target_word',
                        'part_of_speech', 'definition', 'prefix'],
                condition=models.Q(part_of_speech__isnull=False) &
                models.Q(definition__isnull=False) &
                models.Q(prefix__isnull=False),
            ),
            models.UniqueConstraint(
                name='unique_translation_minimal',
                fields=['source_word', 'target_word'],
                condition=models.Q(part_of_speech__isnull=True) &
                models.Q(definition__isnull=True) &
                models.Q(prefix__isnull=True),
            )
        ]

    def __str__(self):
        return f"[{self.pk}] {self.source_word.word} [{self.part_of_speech} \ {self.source_word.language.name}] -> {self.target_word.word} [{self.part_of_speech} \ {self.target_word.language.name}]"


class WordDetail(models.Model):
    word = models.OneToOneField(
        Word,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Слово',
        help_text='Слово, для которого создаются детали.'
    )
    transcription = models.CharField(
        max_length=70,
        blank=True,
        null=True,
        verbose_name='Транскрипция',
        help_text='Транскрипция слова.'
    )
    audio_url = models.URLField(
        blank=True,
        verbose_name='Аудиофайл',
        help_text='Ссылка на аудиофайл слова.'
    )

    def __str__(self):
        return f'[{self.pk}] {self.word} details'

    class Meta:
        abstract = True


class EnglishWordDetail(WordDetail):

    class Meta:
        verbose_name = 'Eng | Детали'
        verbose_name_plural = 'Eng | Детали'


class FrenchWordDetail(WordDetail):
    GENDERS = {
        'm': 'Мужской',
        'f': 'Женский',
        'n': 'Средний'
    }
    genus = models.CharField(
        max_length=1,
        choices=GENDERS,
        blank=True,
        null=True,
        verbose_name='Род',
        help_text='Род слова.'
    )

    class Meta:
        verbose_name = 'Fr | Детали'
        verbose_name_plural = 'Fr | Детали'


class SpanishWordDetail(WordDetail):
    class Meta:
        verbose_name = 'Sp | Детали'
        verbose_name_plural = 'Sp | Детали'


# class RussianWordDetail(models.Model):
#     word = models.ForeignKey(
#         Word,
#         on_delete=models.CASCADE,
#         related_name='%(class)s',
#         verbose_name='Слово',
#         help_text='Слово, для которого создаются детали.'
#     )
#     image_url = models.URLField(
#         blank=True,
#         null=True,
#         verbose_name='Изображение',
#         help_text='Ссылка на изображение слова.'
#     )

#     def __str__(self):
#         return f'[{self.pk}] {self.word} details'

#     class Meta:
#         verbose_name = 'Ru | Детали'
#         verbose_name_plural = 'Ru | Детали'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['word', 'image_url'],
#                 name='unique_word_image_url',
#                 condition=~models.Q(image_url='') & ~models.Q(image_url=None),
#             ),
#         ]


class EnglishVerb(models.Model):
    infinitive = models.OneToOneField(
        verbose_name='Инфинитив',
        to=Word,
        on_delete=models.SET_NULL,
        related_name='en_verb',
        blank=True,
        null=True,
        limit_choices_to={'language': 1}
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
        verbose_name = 'Eng | Глагол'
        verbose_name_plural = 'Eng | Глаголы'

        ordering = ['infinitive__word']


class FrenchVerb(models.Model):
    infinitive = models.OneToOneField(
        verbose_name='Инфинитив',
        to=Word,
        on_delete=models.SET_NULL,
        related_name='fr_verb',
        blank=True,
        null=True,
        limit_choices_to={'language': 3}
    )
    participe_present = models.CharField(
        verbose_name='Причастие настоящего времени',
        max_length=50,
    )
    participe_passe = models.CharField(
        verbose_name='Причастие прошедшего времени',
        max_length=50,
    )
    indicatif_j = models.CharField(
        verbose_name='Indicatif présent je',
        max_length=50,
    )
    indicatif_tu = models.CharField(
        verbose_name='Indicatif présent tu',
        max_length=50,
    )
    indicatif_il = models.CharField(
        verbose_name='Indicatif présent il/elle',
        max_length=50,
    )
    indicatif_nous = models.CharField(
        verbose_name='Indicatif présent nous',
        max_length=50,
    )
    indicatif_vous = models.CharField(
        verbose_name='Indicatif présent vous',
        max_length=50,
    )
    indicatif_ils = models.CharField(
        verbose_name='Indicatif présent ils/elles',
        max_length=50,
    )

    def __str__(self) -> str:
        return f'{self.infinitive.word if self.infinitive else self.infinitive} - {self.participe_present} - {self.participe_passe}'

    class Meta:
        verbose_name = 'Fr | Глагол'
        verbose_name_plural = 'Fr | Глаголы'

        ordering = ['infinitive__word']
