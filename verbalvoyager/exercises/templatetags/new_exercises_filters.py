import re

from random import shuffle
from django.utils.safestring import mark_safe

from django import template

register = template.Library()


@register.filter(name="sentences_split", is_safe=True)
def sentences_split(values):
    return values.split('\r\n')


@register.filter(name="get_shuffled_translates", is_safe=True)
def get_shuffled_translates(values, lang=None):
    if lang == 'russian':
        translates = [{'idx': idx + 1, 'word': word['word']}
                      for idx, word in enumerate(values)]
        shuffle(translates)
    else:
        translates = [{'idx': idx + 1, 'translation': word['translation']}
                      for idx, word in enumerate(values)]
        shuffle(translates)
    return translates


@register.filter(name="get_words_list")
def get_words_list(values):
    return values.split(' ')


@register.filter(name="shuffle")
def shiffle_(values):
    if isinstance(values, list):
        values = values[0]

    values = list(values)
    shuffle(values)
    return ''.join(values)


@register.filter(name="parse_to_list", is_safe=True)
def parse_to_list(values):
    result = ''

    for word in list(values):
        result += f'<li><p class="text">{word.capitalize()}</p></li>'

    return mark_safe(result)


@register.filter(name="str_to_list")
def str_to_list(values):
    try:
        return eval(values)
    except SyntaxError:
        return


@register.filter(name="highlight", is_safe=True)
def highlight(values):
    pattern = r'\[[\w\s]+\]'
    is_match = re.search(pattern, values)

    if is_match:
        values = values.replace(
            is_match[0],
            f"<span class='example-word'>{is_match[0][1:-1]}</span>"
        )
    return mark_safe(values)


@register.filter
def get_word_details(word):
    match word.language.name:
        case 'English':
            return word.englishworddetail
        case 'Russian':
            return word.russianworddetail.first()
