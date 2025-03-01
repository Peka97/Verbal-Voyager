from django.db.utils import DataError
from requests.exceptions import JSONDecodeError
# from dictionary.models import EnglishWord, FrenchWord, IrregularEnglishVerb
from verbalvoyager.settings import OPENAI_API_KEY
from pprint import pprint
import requests
import re
import os
import django
# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()


# def update_words(words):
#     from django.db import transaction
#     fields = [field for field in words[0].keys(
#     ) if field not in ('id', 'meaning_id', 'word')]
#     for word in words:
#         # del word['id']
#         del word['meaning_id']
#         print(f"{word['word']} - {word['translation']}")
#         # del word['word']

#     with transaction.atomic():
#         EnglishWord.objects.bulk_update(
#             [EnglishWord(**word) for word in words], fields)


# def create_or_update(words):
#     from django.db import transaction
#     from django.db.utils import IntegrityError
#     from django.core.exceptions import ValidationError

#     with transaction.atomic():
#         for word in words.values():
#             # print(word)
#             try:
#                 word_obj, was_created = EnglishWord.objects.get_or_create(
#                     **word
#                 )

#                 if was_created:
#                     print(f'[CREATE] Word "{word_obj}" was created')
#                 else:
#                     print(
#                         f'[UPDATE] Word "{word_obj}" was not created. Updated means')

#                 word_obj.save()

#             except (ValidationError, IntegrityError):
#                 pass

#             except DataError as err:
#                 pprint(word)
#                 print(err)
#                 exit(1)

#             except EnglishWord.MultipleObjectsReturned:
#                 print(
#                     f'Error: Multiple objects returned for word "{word["word"]}"')
#                 # exit(1)


def load_words_meaning_ids_from_api(words):
    words_to_edit = []
    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?pageSize=1'
    headers = {'accept': 'application/json'}
    params = {}

    for word in words:
        # if word['prefix'] or '(' in word['word'] or '/' in word['word']:
        #     continue

        params['search'] = word['word']

        try:
            resp = requests.get(url, params, headers=headers)
            # print(resp.json())
            resp_json = resp.json()[0]
        except IndexError:
            print(resp.json())
            print(f'Error: {word}')
            words_to_edit.append(word)
        else:
            word['meaning_id'] = (str(resp_json[0]['meanings'][0]['id']))
            # print(word['meaning_id'])

    # print(words)

    words = [word for word in words if word.get('meaning_id') is not None]
    return words, words_to_edit


def load_words_meanings_from_api(words):
    url = 'https://dictionary.skyeng.ru/api/public/v1/meanings'
    headers = {'accept': 'application/json'}
    params = {'ids': ','.join(
        [
            word['meaning_id']
            for word in words
        ]
    )}

    try:
        resp = requests.get(url, params, headers=headers)
        resp_json = resp.json()
        pprint(resp_json)

    except IndexError:
        # print(resp.json())
        pass
    else:
        # pprint(resp_json)
        for word, word_api in zip(words, resp_json):
            word['speech_code'] = word_api['partOfSpeechCode']
            # [{'soundUrl': 'url_to_definition_sound', 'text': 'definition text'}]
            word['definition'] = word_api['definition']['text']
            # [{'soundUrl': 'url_to_example_sound', 'text': 'example text'}]
            word['examples'] = [example['text']
                                for example in word_api['examples']]
            try:
                # [{'url': 'url_to_image.jpeg'},]
                word['image_url'] = word_api['images'][0]['url']

                pattern = re.compile(r'/\d{3}x\d{3}/')
                image_size = re.search(pattern, word['image_url'])
                if word['image_url'] and image_size:
                    word['image_url'] = word['image_url'].replace(
                        image_size[0], '/640x480/')
            except IndexError:
                word['image_url'] = None

            word['prefix'] = word_api['prefix']
            word['sound_url'] = word_api['soundUrl']
            word['transcription'] = word_api['transcription']
            if word_api['translation']['text']:
                # {'note': note, 'text': text}
                word['translation'] = word_api['translation']['text']
            word['another_means'] = []
            for mean in word_api['meaningsWithSimilarTranslation']:
                if mean['translation'].get('note'):
                    word['another_means'].append(
                        f"{mean['translation']['text']} ({mean['translation']['note']})"
                    )
                else:
                    word['another_means'].append(mean['translation']['text'])

            print(f"{word['word']} - {word['translation']}")

    # pprint(words)
    return words


def load_words_all_meaning_ids_from_api(words):
    words_to_edit = []
    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search'
    headers = {'accept': 'application/json'}
    params = {}

    for word in words:
        params['search'] = word['word']

        try:
            resp = requests.get(url, params, headers=headers)
            resp_json = resp.json()
            # print(f"Response: {resp.json()}")
        except (KeyError, IndexError):
            print(f'Error: {word}')

            print(f"Response: {resp.json()}")
            words_to_edit.append(word)
        else:
            for word_info in resp_json:
                # pprint(word_info)

                word['meaning_id'] = []
                meanings = word_info['meanings']

                for mean in meanings:
                    # pprint(mean)

                    if len(mean['transcription']) > 100 or len(mean['translation']['text']) > 100 or len(mean['soundUrl']) > 300:
                        print(f"[SKIP] {word['word']} - {word['translation']}")
                        continue
                    if mean['translation']['text'] == word['translation']:
                        print(f"[SKIP] {word['word']} - {word['translation']}")
                        continue
                    word['meaning_id'].append(str(mean['id']))

    words = [word for word in words if word.get('meaning_id') is not None]
    return words, words_to_edit


def load_words_all_meanings_from_api(words):
    url = 'https://dictionary.skyeng.ru/api/public/v1/meanings'
    headers = {'accept': 'application/json'}
    mean_ids = []
    for word in words:
        mean_ids.extend(word['meaning_id'])
    params = {'ids': ','.join(mean_ids)}

    try:
        resp = requests.get(url, params, headers=headers)
        resp_json = resp.json()
        # print(resp_json)
        # pprint(resp_json)

    except (IndexError, JSONDecodeError):
        print(resp.text())
    else:
        result = {mean_id: {} for mean_id in mean_ids}
        # print(result)
        # pprint(resp_json)
        for word_api in resp_json:
            word = result[word_api['id']]

            word['speech_code'] = word_api['partOfSpeechCode']
            # [{'soundUrl': 'url_to_definition_sound', 'text': 'definition text'}]
            word['definition'] = word_api['definition']['text']
            # [{'soundUrl': 'url_to_example_sound', 'text': 'example text'}]
            word['examples'] = [example['text']
                                for example in word_api['examples']]
            try:
                # [{'url': 'url_to_image.jpeg'},]
                word['image_url'] = word_api['images'][0]['url']

                pattern = re.compile(r'/\d{3}x\d{3}/')
                image_size = re.search(pattern, word['image_url'])
                if word['image_url'] and image_size:
                    word['image_url'] = word['image_url'].replace(
                        image_size[0], '/640x480/')
            except IndexError:
                word['image_url'] = None

            word['prefix'] = word_api['prefix']
            word['sound_url'] = word_api['soundUrl']
            word['transcription'] = word_api['transcription']
            word['word'] = word_api['text']
            if word_api['translation']['text']:
                # {'note': note, 'text': text}
                word['translation'] = word_api['translation']['text']
            # word['another_means'] = []
            # for mean in word_api['meaningsWithSimilarTranslation']:
            #     if mean['translation'].get('note'):
            #         word['another_means'].append(
            #             f"{mean['translation']['text']} ({mean['translation']['note']})"
            #         )
            #     else:
            #         word['another_means'].append(mean['translation']['text'])

            # pprint(result)

        return result


# def turn_word_to_lowercase(word_object: EnglishWord | FrenchWord):
#     words_obj = word_object.objects.all()
#     words = words_obj.values()
#     for word in words:
#         word['word'] = word['word'].lower()
#         word['translation'] = word['translation'].lower()

#     from django.db import transaction

#     fields = ('word', 'translation')

#     with transaction.atomic():
#         word_object.objects.bulk_update(
#             [word_object(**word) for word in words], fields)


# def find_words_dulicates(word_object: EnglishWord | FrenchWord):
#     from django.db.models import Count
#     duplicates = word_object.objects.values('word', 'translation').annotate(
#         count=Count('id')).filter(count__gt=1).order_by()

#     words_duplicates = [word['word'] for word in duplicates]
#     translation_duplicates = [word['translation'] for word in duplicates]

#     duplicates_objects = word_object.objects.filter(
#         word__in=words_duplicates, translation__in=translation_duplicates).all()
#     return duplicates_objects


if __name__ == '__main__':
    from exercises.models import ExerciseEnglishWords

    # exercise = ExerciseEnglishWords.objects.get(pk=1)
    # words_obj = exercise.words.all()
    # words = exercise.words.all().values()
    # words_obj = EnglishWord.objects.all()

    # words = words_obj.values()
    # start_idx = 0

    # while start_idx + 100 <= len(words):
    #     end_idx = start_idx + 100
    #     part_words = words[start_idx:end_idx]

    #     print(f"Start {start_idx} - {end_idx}")

    #     part_words, words_to_edit = load_words_meaning_ids_from_api(part_words)
    #     if part_words:
    #         part_words = load_words_meanings_from_api(part_words)
    #         update_words(part_words)

    #     print(f"Done {start_idx} - {end_idx}")

    #     start_idx = end_idx

    # part_words = words[start_idx:]

    # part_words, words_to_edit = load_words_meaning_ids_from_api(part_words)
    # part_words = load_words_meanings_from_api(part_words)
    # update_words(part_words)

    # from django.db.models.functions import Length
    # from django.db.models import F

    # words_obj = EnglishWord.objects.annotate(column_length=Length(F('transcription'))).filter(column_length__gt=75)
    # words=words_obj.all()
    # pprint(words)
    # words.delete()

    from dictionary.models import EnglishWord, FrenchWord, IrregularEnglishVerb

    words_obj = EnglishWord.objects.filter(word__startswith='(').all()
    for word in words_obj:
        print(word)
        print(word.word.split(')')[1:][0].lstrip())
        # word.word = word.word.split(')')[1:][0].lstrip()
        # word.save()
        # word.save()

        # word.definition = word.definition.split('.')[0]
        # word.save()
        # print(f"{word.word} => {word.word.strip()}")
        # try:
        #     word.word = word.word.strip()
        #     word.save()
        # except django.core.exceptions.ValidationError:
        #     word.delete()

    # words = words_obj.values()

    # result, _ = load_words_all_meaning_ids_from_api(words)
    # result = load_words_all_meanings_from_api(result)
    # pprint(result)
    # create_or_update(result)

    # words_obj = EnglishWord.objects.all()[35000:]
    # from django.db import transaction
    # print(f"Total: {words_obj.count()} words")

    # start_idx = 0
    # step = 100

    # while start_idx + step <= len(words_obj):
    #     end_idx = start_idx + step
    #     words = words_obj[start_idx:end_idx]

    #     with transaction.atomic():
    #         for word in words:
    #             word.save()

    #     print(f"From {start_idx} to {end_idx} saved.")

    #     start_idx = end_idx

    # from django.db import transaction

    # words_obj = EnglishWord.objects.all()[35000:]
    # with transaction.atomic():
    #         for word in words_obj:
    #             word.save()

    # print(words_obj.count())
    # # result, _ = load_words_all_meaning_ids_from_api(words)
    # # # pprint(result)
    # # result = load_words_all_meanings_from_api(result)
    # # # pprint(result)
    # # create_or_update(result)

    # words_obj = EnglishWord.objects.all()[7100 + 3860:]
    # words = words_obj.values()
    # print(f'Words count: {words_obj.count()}')

    # start_idx = 0
    # step = 10

    # while start_idx + step <= len(words):
    #     end_idx = start_idx + step
    #     part_words = words[start_idx:end_idx]

    #     print(f"Start {start_idx} - {end_idx}")

    #     result, _ = load_words_all_meaning_ids_from_api(part_words)
    #     # pprint(result)
    #     if result:
    #         result = load_words_all_meanings_from_api(result)
    #         # pprint(result)
    #         create_or_update(result)

    #     print(f"Done {start_idx} - {end_idx}")

    #     start_idx = end_idx
    #     # break

    # part_words = words[start_idx:]

    # result, _ = load_words_all_meaning_ids_from_api(part_words)
    # result = load_words_all_meanings_from_api(result)
    # create_or_update(result)
