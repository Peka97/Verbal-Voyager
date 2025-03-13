import json
import requests
import re
from pprint import pprint

from django.shortcuts import render
from django.http import JsonResponse

from .models import EnglishWord


def load_from_api(request, lang):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word')
        word_id = data.get('word_id')
        translation = data.get('translation')

        check_fields = {}

        if word:
            check_fields['word'] = word.lower()
        if translation:
            check_fields['translation'] = translation.lower()

        if word and translation:
            word_check = EnglishWord.objects.filter(
                **check_fields)

            if word_check.exists():
                word_check_obj = word_check.first()

                if not word_id:
                    return JsonResponse({'error': f'Слово уже есть в словаре: ID {word_check_obj.pk}.'}, status=409)
                elif word_check_obj.word == word and word_check_obj.translation == translation and str(word_check_obj.pk) != str(word_id):
                    return JsonResponse({'error': f'Слово уже есть в словаре: ID {word_check_obj.pk}.'}, status=409)

        url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?pageSize=1'
        headers = {'accept': 'application/json'}
        params = {
            'search': word,
        }

        try:
            resp = requests.get(url, params, headers=headers)
            resp_json = resp.json()[0]
        except IndexError:
            return JsonResponse({'error': 'Не найдено. Проверьте правильность ввода.'}, status=404)

        for mean in resp_json['meanings']:
            if mean['translation']['text'] == translation:

                url = 'https://dictionary.skyeng.ru/api/public/v1/meanings'
                headers = {'accept': 'application/json'}
                params = {
                    'ids': mean['id']
                }

                try:
                    resp = requests.get(url, params, headers=headers)
                    resp_json = resp.json()

                except IndexError:
                    return JsonResponse({'error': 'Не найдено. Проверьте правильность ввода.'}, status=404)
                else:
                    word_api = resp_json[0]

                    answer = {
                        'word': word,
                        'translation': translation,
                    }

                    answer['speech_code'] = word_api['partOfSpeechCode']
                    answer['definition'] = word_api['definition']['text']
                    answer['examples'] = [example['text']
                                          for example in word_api['examples']]
                    try:
                        answer['image_url'] = word_api['images'][0]['url']

                        pattern = re.compile(r'/\d{3}x\d{3}/')
                        image_size = re.search(pattern, answer['image_url'])
                        if answer['image_url'] and image_size:
                            answer['image_url'] = answer['image_url'].replace(
                                image_size[0], '/640x480/')
                    except IndexError:
                        answer['image_url'] = None

                    pprint(word_api)
                    answer['prefix'] = word_api['prefix']
                    answer['sound_url'] = word_api['soundUrl']
                    answer['transcription'] = word_api['transcription']
                    answer['another_means'] = []

                    for mean_api in word_api['meaningsWithSimilarTranslation']:
                        if mean_api['translation'].get('note'):
                            answer['another_means'].append(
                                f"{mean_api['translation']['text']} ({mean_api['translation']['note']})"
                            )
                        else:
                            answer['another_means'].append(
                                mean_api['translation']['text'])

                    return JsonResponse(answer, status=200)

        answer = {
            'means': [
                mean['translation']['text']
                for mean in resp_json['meanings']
            ]
        }

        return JsonResponse(answer, status=200)
