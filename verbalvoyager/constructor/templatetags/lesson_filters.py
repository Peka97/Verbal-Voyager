
from django import template


register = template.Library()

# TODO: пока нет возможности выбрать изучаемый перевод слова.
# Нужно подумать над адаптацией упражнения


@register.filter
def get_word_text(word_id):
    from dictionary.models import Word
    word = Word.objects.get(id=word_id)
    return word.word


@register.filter
def process_sentence(sentence):
    sentence = sentence.replace('[', '').replace(']', '')
    sentence = sentence.split(' ')
    # shuffle(sentence)
    return sentence
