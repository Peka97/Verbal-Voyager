import requests

from django.db.utils import IntegrityError

from dictionary.models import Word, Language, Translation, EnglishWordDetail, RussianWordDetail

english_lang, _ = Language.objects.get_or_create(name='English')
russian_lang, _ = Language.objects.get_or_create(name='Russian')


def load_from_api(word: Word):
    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?pageSize=1'
    headers = {
        'accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    params = {
        'search': word.word,
    }

    resp = requests.get(url, params, headers=headers).json()

    if not resp:
        return

    word_api_word = resp[0]

    for mean in word_api_word['meanings']:
        # if mean['translation']['text'] == translation:

        url = 'https://dictionary.skyeng.ru/api/public/v1/meanings'
        headers = {'accept': 'application/json'}
        params = {
            'ids': mean['id']
        }

        resp = requests.get(url, params, headers=headers).json()

        if not resp:
            continue

        word_api_mean = resp[0]

        examples = word_api_mean.get('examples')
        image_url = word_api_mean['images'][0]['url'] if word_api_mean['images'] and len(
            word_api_mean['images'][0]['url']) < 200 else None
        part_of_speech = word_api_mean['partOfSpeechCode']
        prefix = word_api_mean.get('prefix')
        audio_url = word_api_mean.get('soundUrl') if len(
            word_api_mean.get('soundUrl')) < 200 else None
        transcription = word_api_mean.get('transcription')
        if word_api_mean['translation'] and word_api_mean['translation']['text']:
            translation = word_api_mean['translation']['text'] if len(
                word_api_mean['translation']['text']) < 50 else word_api_mean['translation']['text'][:50]
        else:
            translation = None
        definition = word_api_mean['definition']['text'] if word_api_mean['definition'] else None

        # print(f"""
        #     [Word] {word.word}
        #     - [Translation] {translation}
        #     - [Transcription] {transcription}

        #     - [Part of speech] {part_of_speech}
        #     - [Prefix] {prefix}

        #     - [Definition] {definition}
        #     - [Examples] {examples}

        #     - [Image] {image_url}
        #     - [Audio] {audio_url}
        #     """)

        print(f"[English word] {word.word} [Russian word] {translation}")

        eng_word = word

        try:
            eng_word_detail = safe_get_or_create(
                EnglishWordDetail,
                word=eng_word,
                transcription=transcription,
                audio_url=audio_url,
            )

            ru_word = safe_get_or_create(
                Word,
                word=translation,
                language=russian_lang,
            )

            ru_word_detail = safe_get_or_create(
                RussianWordDetail,
                word=ru_word,
                image_url=image_url
            )

            eng_word_translation = safe_get_or_create(
                Translation,
                source_word=eng_word,
                target_word=ru_word,
                part_of_speech=part_of_speech,
                definition=definition,
                examples=examples,
                prefix=prefix,
            )
        except IntegrityError:
            print(f"[Error] {word.word} - {translation}")
            continue


def safe_get_or_create(model, **kwargs):
    obj = model.objects.filter(**kwargs)

    if not obj.exists():
        obj = model.objects.create(**kwargs)
        obj.save()
    else:
        obj = obj.first()

    return obj
