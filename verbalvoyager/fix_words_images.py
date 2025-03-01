import os
import django
# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()


if __name__ == "__main__":
    from dictionary.models import EnglishWord
    
    words = EnglishWord.objects.all()
    words_values = words.values()
    for word in words:
        if word.image_url and '200x150' in word.image_url:
            word.image_url = word.image_url.replace('200x150', '640x480')
            word.save()
