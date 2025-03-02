import json
import os
import django

if __name__ == '__main__':
    # Django setup
    os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
    django.setup()

    from exercises.models import EnglishWord

    EnglishWord.objects.all().delete()

    words_list = []

    with open('dump_prod_words.json', 'r') as f:
        words = json.load(f)
        for word in words:
            obj_word = word['fields']
            obj_word['pk'] = word['pk']
            del obj_word['lang']

            words_list.append(EnglishWord(**obj_word))

    # print(words_list)

    # Django setup
    os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
    django.setup()

    from exercises.models import EnglishWord
    from django.db import transaction

    with transaction.atomic():
        EnglishWord.objects.bulk_create(words_list)
