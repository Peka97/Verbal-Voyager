import os
import logging

import django

# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()

# Logger setup
logger = logging.getLogger(__file__)
logger.addHandler(
    logging.FileHandler(
        '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/load_words.log'
    )
)
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    from exercises.models import Word

    problem_words = list(Word.objects.filter(word__contains=', ').all())
    problem_translate = list(Word.objects.filter(
        translate__contains=', ').all())
    for word in problem_words:
        if '(' in word.word:
            correct_word = word.word.split(' (')[0]
            if ', ' in correct_word:
                correct_word = correct_word.split(', ')[0]
        else:
            correct_word = word.word.split(', ')[0]
        word.word = correct_word
        word.save()

    for word in problem_translate:
        if '(' in word.translate:
            correct_translate = word.translate.split(' (')[0]
            if ', ' in correct_translate:
                correct_translate = correct_translate.split(', ')[0]
        else:
            correct_translate = word.translate.split(', ')[0]
        word.translate = correct_translate
        word.save()
