import json
import logging
import requests
import re

from django.http import JsonResponse

from .models import EnglishWord
from .utils import get_word_class_name

logger = logging.getLogger('django')


def load_from_api(request, lang):
    if request.method != 'POST':
        return

    data = json.loads(request.body)
    word_id, word, translation = load_word_data(data)

    if word and translation:
        word_check = EnglishWord.objects.filter(
            word=word, translation=translation)

        if word_check.exists():
            word_check_obj = word_check.first()

            if not word_id or \
                    (
                        word_check_obj.word == word and
                        word_check_obj.translation == translation and
                        str(word_check_obj.pk) != str(word_id)
                    ):
                return JsonResponse({'error': f'Слово уже есть в словаре: ID {word_check_obj.pk}.'}, status=409)

    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?pageSize=1'
    headers = {'accept': 'application/json'}
    params = {'search': word, }

    try:
        resp = requests.get(url, params, headers=headers)
        resp_json = resp.json()[0]
    except IndexError:
        return JsonResponse({'error': 'Не найдено. Проверьте правильность ввода.'}, status=404)

    meanings = resp_json['meanings']
    means = [mean['translation']['text'] for mean in meanings]

    if translation not in means:
        return JsonResponse({'means': means}, status=200)

    for mean in meanings:
        if mean['translation']['text'] != translation:
            continue

        url = 'https://dictionary.skyeng.ru/api/public/v1/meanings'
        headers = {'accept': 'application/json'}
        params = {'ids': mean['id']}

        try:
            resp = requests.get(url, params, headers=headers)
            resp_json = resp.json()

        except IndexError:
            return JsonResponse({'error': 'Не найдено. Проверьте правильность ввода.'}, status=404)

        else:
            answer = {
                'word': word,
                'translation': translation,
            }
            answer = parse_word_data(resp_json[0], answer)

            return JsonResponse(answer, status=200)


def load_word_data(data):
    word_id = data.get('word_id')
    word = data.get('word').lower() if data.get('word') else None
    translation = data.get('translation').lower() \
        if data.get('translation') else None
    return word_id, word, translation


def parse_word_data(word_api, answer):
    answer['speech_code'] = word_api['partOfSpeechCode']
    answer['definition'] = word_api['definition']['text']
    answer['prefix'] = word_api['prefix']
    answer['sound_url'] = word_api['soundUrl']
    answer['transcription'] = word_api['transcription']
    answer['another_means'] = []
    answer['examples'] = [
        example['text']
        for example in word_api['examples']
    ]

    try:
        answer['image_url'] = word_api['images'][0]['url']

        pattern = re.compile(r'/\d{3}x\d{3}/')
        image_size = re.search(pattern, answer['image_url'])
        if answer['image_url'] and image_size:
            answer['image_url'] = answer['image_url'].replace(
                image_size[0], '/640x480/')
    except IndexError:
        answer['image_url'] = None

    for mean_api in word_api['meaningsWithSimilarTranslation']:
        if mean_api['translation'].get('note'):
            answer['another_means'].append(
                f"{mean_api['translation']['text']} ({mean_api['translation']['note']})"
            )
        else:
            answer['another_means'].append(
                mean_api['translation']['text'])
    return answer


def get_translation(request, lang):
    if request.method == 'POST':
        try:
            words = json.loads(request.body)
            print(words)

            result = {}
            word_object = get_word_class_name(lang)
            for word in words:
                word_qs = word_object.objects.filter(word=word)
                if word_qs.exists():
                    result[word] = {
                        'id': word_qs.first().id,
                        'translations': [
                            word_obj.translation for word_obj in word_qs.all()]
                    }

            return JsonResponse({'result': result}, status=200)
        except Exception as e:
            logger.error(f'Error getting translation: {e}', exc_info=True)
            return JsonResponse({'message': 'Что-то пошло не так.'}, status=500)
