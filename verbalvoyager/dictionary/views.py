import json
import logging
import requests
import re
from pprint import pprint

from django.http import JsonResponse
from django.db.models import Q

from .models import EnglishWord, Language, Translation, Word, EnglishWordDetail, RussianWordDetail
from .utils import get_word_class_name

logger = logging.getLogger('django')


def load_from_api(request):
    print(request)
    if request.method != 'POST':
        return JsonResponse({"error": f"Wrong method: {request.method}."}, status=405)

    if not request.body:
        return JsonResponse({'error': 'No data.'}, status=400)

    data = json.loads(request.body)
    translation_id, source_word_id, target_word_id = load_word_data(data)

    if not source_word_id:
        return JsonResponse({'error': 'No source word.'}, status=400)

    print(translation_id, source_word_id, target_word_id)

    if source_word_id and target_word_id:
        word_check = Translation.objects.filter(
            source_word=source_word_id, target_word=target_word_id)

        if word_check.exists():
            return JsonResponse({'error': f'Слово уже есть в словаре: ID {word_check.first().pk}.'}, status=409)

    source_word_obj = Word.objects.get(pk=source_word_id)

    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?pageSize=1'
    headers = {'accept': 'application/json'}
    params = {'search': source_word_obj.word, }

    try:
        resp = requests.get(url, params, headers=headers)
        resp_json = resp.json()[0]
        pprint(resp_json)
    except IndexError:
        return JsonResponse({'error': 'Не найдено. Проверьте правильность ввода.'}, status=404)

    meanings = resp_json['meanings']
    means = [mean['translation']['text'] for mean in meanings]

    if not target_word_id:
        return JsonResponse({'means': means}, status=200)

    target_word_obj = Word.objects.get(pk=target_word_id)

    for mean in meanings:
        if mean['translation']['text'].lower() != target_word_obj.word:
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
                'word': source_word_obj.word,
                'translation': target_word_obj.word,
            }
            answer = parse_word_data(resp_json[0], answer)
            create_word_details(source_word_obj.pk, answer)
            create_word_details(target_word_obj.pk, answer)

            return JsonResponse(answer, status=200)

    return JsonResponse({'means': means}, status=200)


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
    answer['examples'] = word_api['examples']

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
            # print(lang)

            result = {}

            for word in words:
                lang_obj = Language.objects.get(name='English')

                # in future need add for russian lang
                if lang != 'russian':
                    translation_qs = Translation.objects.filter(
                        source_word__word=word, source_word__language=lang_obj)
                    translation = translation_qs.first()

                if translation_qs.exists():
                    result[word] = {
                        'wordID': translation.source_word.pk,
                        'translations': [
                            {
                                'id': translation.pk,
                                'translation': translation.target_word.word
                            }
                            for translation in translation_qs.all()
                        ]
                    }

            return JsonResponse({'result': result}, status=200)
        except Exception as e:
            logger.error(f'Error getting translation: {e}', exc_info=True)
            return JsonResponse({'message': 'Что-то пошло не так.'}, status=500)


def create_word_details(word_id, data):
    word = Word.objects.get(pk=word_id)

    match word.language.name:
        case 'English':
            if EnglishWordDetail.objects.filter(word=word).exists():
                details = EnglishWordDetail.objects.get(word=word)
            else:
                details = EnglishWordDetail(
                    word=word,
                )
            details.transcription = data.get('transcription')
            details.audio_url = data.get('sound_url')
        case 'French':
            # пока не реализовано
            return
        case 'Spanish':
            # пока не реализовано
            return
        case 'Russian':
            if RussianWordDetail.objects.filter(word=word).exists():
                details = RussianWordDetail.objects.get(word=word)
            else:
                details = RussianWordDetail(
                    word=word,
                )
            details.image_url = data.get('image_url')
        case _:
            return None

    details.save()
    return details
