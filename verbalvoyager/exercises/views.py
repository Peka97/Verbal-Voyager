import json
import requests
import logging
from random import sample, shuffle

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import Exercise, Word, ExerciseResult

log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(DEBUG_LOGGING_FP)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

User = get_user_model()


@login_required(login_url="/users/auth")
def exercises_words(request, ex_id, step):
    titles = {1: 'Запоминаем', 2: 'Выбираем', 3: 'Расставляем', 4: 'Переводим'}
    user = User.objects.get(username=request.user.username)

    try:
        exercise = list(Exercise.objects.filter(
            pk=ex_id,
            student=user
        ).all())[0]
    except IndexError:
        method = request.META['REQUEST_METHOD']
        url = request.META['PATH_INFO']
        user = request.user.username
        msg = f"Forbidden: {method} - {url} - {user}"
        logger.error(msg)

        return redirect('err_404')

    words = get_words(exercise)
    # logger.info(f'Word count: {len(words)}')
    # logger.info(f'Words: {words}')

    template_name = f'exercises/exercise_step_{step}.html'
    context = {
        'ex_id': ex_id,
        'step': step,
        'title': titles[step],
        'words': words,
        'shuffled_translates': get_shuffled_translates(list(exercise.words.all())),
        'len': range(1, len(words) + 1)
    }

    if step == 1:
        # logger.info(context['words'][0])
        if context['words'][0]['lang'] != 'eng':
            pass
        else:
            api_words = get_api_for_words(words)

            for word, api_word in zip(context['words'], api_words):
                word['api'] = api_word

    # logger.info(f"Word count: {len(context['words'])}")
    # logger.info(f"Words: {context['words']}")
    # if request.user.username == 'peka97' and step == '3':
    #     template_name = 'exercises/exercise_step_3_test.html'

    return render(request, template_name, context)


def get_words(exercise: list[Exercise]):  # list[Exercise]
    result = []
    words = list(exercise.words.all())

    # logger.info(f'Words len: {len(words)}')
    # logger.info(f'Words from DB: {words}')

    for idx, word in enumerate(words):

        if word.sentences:

            if '\n' in word.sentences:
                sentences = word.sentences.split('\n')
            else:
                sentences = [word.sentences]

        else:
            sentences = word.sentences

        data = {
            'id': idx + 1,
            'lang': word.lang,
            'word': word.word,
            'translate': word.translate,
            'sentences': sentences,
            'translate_vars': get_translate_vars(words, word),
        }
        result.append(data)

    return result


def get_shuffled_translates(words: list[Word]) -> list[dict]:  # list[Word]
    translates = [{'id': idx + 1, 'trans': word.translate}
                  for idx, word in enumerate(words)]
    shuffle(translates)
    return translates


def get_translate_vars(words: list[Word], word: str):  # list[Word]
    ex_words = [word.translate for word in words]
    del ex_words[ex_words.index(word.translate)]

    if len(words) > 4:
        words = sample(ex_words, 3)
    else:
        words = sample(ex_words, len(words) - 1)

    words.append(word.translate)
    shuffle(words)
    return words


@login_required
def update(request, ex_id, step_num):
    if request.method == 'POST':
        logger.info(
            f'POST REQUEST:\n Ex:{ex_id} | {step_num} | {json.loads(request.body)}'
        )

        data = json.loads(request.body)
        value = data.get('value')

        obj, _ = ExerciseResult.objects.get_or_create(
            exercise=Exercise.objects.get(pk=ex_id),
        )
        obj.__dict__[step_num] = value
        obj.save()

        if step_num[-1] == '4':
            exercise = Exercise.objects.get(pk=ex_id)
            exercise.is_active = False
            exercise.save()

        return redirect('profile')


def get_api_for_words(words: list[Word]):
    img_size = '300x300'
    result = []

    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?search=stone'
    headers = {'accept': 'application/json'}
    params = {'search': ''}

    for word in words:
        params['search'] = word['word']

        try:
            resp = requests.get(url, params, headers=headers).json()[0]
        except IndexError:
            msg = f"\nWord: {word}.\nResp: {requests.get(url, params, headers=headers).text}."
            logger.exception(msg)

            word_text = word['word']
            word_translation = word['translate']
            transcription = None
            image_url = None
            image_url = None
            sound_url = None
        else:
            word_text = resp['text']
            word_translation = resp['meanings'][0]['translation']
            transcription = resp['meanings'][0]['transcription']
            image_url = resp['meanings'][0]['imageUrl']
            image_url = image_url.replace('640x480', img_size)
            sound_url = resp['meanings'][0]['soundUrl']
        finally:
            result.append(
                {
                    'word': word_text,
                    'translation': word_translation,
                    'transcription': transcription,
                    'image_url': image_url,
                    'sound_url': sound_url
                }
            )

    return result
