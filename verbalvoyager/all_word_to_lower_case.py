import os
import django

if __name__ == '__main__':
    # Django setup
    os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
    django.setup()

    from dictionary.models import EnglishWord, FrenchWord

    words_english = EnglishWord.objects.all()
    words_french = FrenchWord.objects.all()

    for word in words_english:
        print(word)
        if word.word:
            word.word = word.word.lower()
        if word.translation:
            word.translation = word.translation.lower()
        word.save()
        print(word)

    for word in words_french:
        print(word)
        word.word = word.word.lower()
        word.translation = word.translation.lower()
        word.save()
        print(word)
