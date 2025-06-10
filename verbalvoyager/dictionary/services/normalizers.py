from django.db.utils import IntegrityError
from django.db.models import Q


from dictionary.models import Word, Translation


def normalize_words(words_qs):
    to_lowercase(words_qs.filter(word__regex=r'^[A-ZА-ЯЁ]'))
    remove_dots(words_qs.filter(word__regex=r'\.$'))
    remove_stars(words_qs.filter(Q(word__endswith=' ***') | Q(word__endswith=' **') |
                 Q(word__endswith=' *')))
    remove_end_spaces(words_qs.filter(word__endswith=' '))
    return words_qs


def to_lowercase(qs):
    for word in qs.all():
        word.word = word.word.lower()
        save_with_update_links(word)


def remove_dots(qs):
    for word in qs.all():
        word.word = word.word.rstrip('.')
        save_with_update_links(word)


def remove_stars(qs):
    for word in qs.all():
        word.word = word.word.replace(
            ' ***', '').replace(' **', '').replace(' *', '')
        save_with_update_links(word)


def remove_end_spaces(qs):
    for word in qs.all():
        word.word = word.word.rstrip()
        save_with_update_links(word)


def save_with_update_links(word):
    try:
        word.save()
    except IntegrityError:
        existing_word = Word.objects.filter(
            word=word.word,
            language=word.language
        ).first()

        if existing_word:
            Translation.objects.filter(
                Q(source_word=word) | Q(target_word=word)
            ).update(
                source_word=existing_word,
                target_word=existing_word
            )
            word.delete()
