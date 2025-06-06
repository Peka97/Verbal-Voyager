from gettext import translation
import re

from random import shuffle
from django.utils.safestring import mark_safe

from django import template
from django.db.models import Prefetch

from dictionary.models import Translation, Word

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

    for word in values:
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
            print(type(word.englishworddetail))
            return word.englishworddetail
        case 'Russian':
            print(type(word.russianworddetail))
            return word.russianworddetail.first()


@register.filter
def set_image_size(image_url, new_width=640, new_height=480):
    pattern = r'(/unsafe/)\d+x\d+'
    replacement = fr'\g<1>{new_width}x{new_height}'
    return re.sub(pattern, replacement, image_url)


@register.filter
def get_another_translates(translation):
    prefetch = Prefetch('target_word', queryset=Word.objects.all())
    another_translations_obj = Translation.objects \
        .filter(source_word=translation.source_word) \
        .exclude(target_word=translation.target_word) \
        .prefetch_related(prefetch).all()
    return [translation.target_word.word for translation in another_translations_obj]


@register.filter
def get_all_translates(translations):
    print([translation.target_word.word for translation in translations])
    return [translation.target_word.word for translation in translations]


@register.filter
def get_random_slice(translations, correct_word):
    if len(translations) <= 4:
        shuffle(translations)
        return translations

    translations.remove(correct_word)
    shuffle(translations)
    translations = translations[:2]
    translations.append(correct_word)
    shuffle(translations)
    return translations


@register.filter
def get_shuffled_values(values):
    shuffle(values)
    return values


@register.filter
def find_translation_id(word, translations):
    match = next(
        (t.target_word.pk for t in translations if t.target_word.word == word),
        None
    )
    if match is None:
        raise ValueError(f"Перевод для слова '{word}' не найден")
    return match
