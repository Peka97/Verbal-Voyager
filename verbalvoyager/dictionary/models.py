from django.db import models


class AbstractWord(models.Model):
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
    
    class Meta:
        abstract = True
        ordering = ['word']

class EnglishWord(AbstractWord):

    def __str__(self) -> str:
        return f'{self.word} - {self.translate}'

    class Meta:
        verbose_name = 'Слово | Eng'
        verbose_name_plural = 'Слова | Eng'

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

    def __str__(self) -> str:
        return f'{self.word} ({self.genus}) - {self.translate}'

    class Meta:
        verbose_name = 'Слово | Fr'
        verbose_name_plural = 'Слова | Fr'