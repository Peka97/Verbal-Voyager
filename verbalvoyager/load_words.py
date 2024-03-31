import os
import requests
import logging
import brotli

import django
from bs4 import BeautifulSoup

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


def get_words(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, utf-8',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code != 200:
        return

    words = []
    text = resp.text
    soup = BeautifulSoup(text, "html.parser")
    table = soup.find('table', id='wordlist').children

    for row in table:
        cells = list(row)

        if cells == ['\n']:
            continue

        word = str(cells[1])[4:-5]
        translate = str(cells[2])[4:-5]

        words.append({'word': word, 'translate': translate})

    return words


def save(word, transtale, lang='eng'):
    try:
        word_in_base = Word.objects.filter(word=word).exists()
        if word_in_base:
            return
        else:
            Word.objects.create(
                word=word,
                translate=transtale,
                lang=lang,
            )
    except BaseException:
        msg = f'Word "{word}" was skipped'
        logger.info(msg)
    # else:
    #     msg = f'Word "{word["word"]}" was added'
    # finally:
    #     logger.info(msg)


def delete():
    words = list(Word.objects.all())
    for word in words:
        Word.objects.get(id=word.pk).delete()


if __name__ == '__main__':
    import csv
    from exercises.models import Word

    # Tests
    # word = {
    #     'word': 'put',
    #     'translate': 'положить',
    #     'sentences': ''
    # }
    # save(word)

    # words = get_words('https://studynow.ru/dicta/allwords')

    with open('/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/Слова для VV.csv', 'r') as words_file:
        reader = csv.reader(words_file, delimiter=';')
        counter = 0

        for line in reader:
            if len(line[0]) < 1 or len(line[1]) < 1:
                continue

            line = line[:2]

            if counter > 10:
                break

            try:
                word = line[0].strip(' ')
                word = word[0].upper() + word[1:]
                translate = line[1].strip(' ')
                translate = translate[0].upper() + translate[1:]
            except IndexError:
                print(word, translate)

            save(word, translate)

            # counter += 1

    # for word in words:
    # save(word)
    # pass

    # delete()
