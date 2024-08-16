import json
import requests
import logging
from random import sample, shuffle

from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from verbalvoyager.settings import DEBUG_LOGGING_FP

from .models import Exercise, Word, ExerciseResult, Dialog

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
    user = request.user
<<<<<<< HEAD

    try:
        exercise = get_object_or_404(Exercise, pk=ex_id, student=user)
    except Http404:
=======
    
    try:
        exercise = Exercise.objects.get(
            pk=ex_id,
            student=user
        )
    except IndexError:
>>>>>>> origin/dev
        method = request.META['REQUEST_METHOD']
        url = request.META['PATH_INFO']
        msg = f"Forbidden: {method} - {url} - {user}"
        logger.error(msg)

        return redirect('err_404')

    words_obj = list(exercise.words.all())
    words = get_words(words_obj)

    template_name = f'exercises/exercise_step_{step}.html'
    context = {
        'ex_id': ex_id,
        'step': step,
        'title': titles[step],
        'words': get_words(words_obj),
        'shuffled_translates': get_shuffled_translates(words_obj),
        'len': range(1, len(words) + 1)
    }

    if step == 1:
<<<<<<< HEAD

=======
        
>>>>>>> origin/dev
        if context['words'][0]['lang'] == 'eng':
            api_words = get_api_for_words(words)

            for word, api_word in zip(context['words'], api_words):
                word['api'] = api_word

    return render(request, template_name, context)


<<<<<<< HEAD
=======
@login_required(login_url="/users/auth")
def exercises_dialog(request, ex_id):
    user = request.user
    
    try:
        dialog = Dialog.objects.get(
            pk=ex_id,
            student=user
        )
        messages = list(filter(lambda s: len(s) > 1, dialog.text.split('\n')))
    except IndexError:
        method = request.META['REQUEST_METHOD']
        url = request.META['PATH_INFO']
        msg = f"Forbidden: {method} - {url} - {user}"
        logger.error(msg)

        return redirect('err_404')
    
    scene = messages[0] if messages[0].startswith('Scene:') else None
    text = messages[1:] if scene else messages
    name_1 = text[0][:text[0].index(':')]
    name_2 = text[1][:text[1].index(':')]
    text = [message.removeprefix(f"{name_1}: ").removeprefix(f"{name_2}: ") for message in text]
    words = dialog.words.all()
    
    context = {
        'scene': scene,
        'text': text,
        'words': get_words(words),
        'name_1': name_1,
        'name_2': name_2,
    }
    return render(request, 'exercises/dialog.html', context)

>>>>>>> origin/dev
def get_words(words: list[Exercise]):
    result = []

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


def get_shuffled_translates(words: list[Word]) -> list[dict]:
    translates = [{'id': idx + 1, 'trans': word.translate}
                  for idx, word in enumerate(words)]
    shuffle(translates)
    return translates


def get_translate_vars(words: list[Word], word: str):
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
def exercises_words_update(request, ex_id, step_num):
    if request.method == 'POST':
        logger.info(
            f'POST REQUEST:\n Ex Words:{ex_id} | {step_num} | {json.loads(request.body)}'
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

@login_required
def exercises_dialog_update(request, ex_id):
    if request.method == 'POST':
        logger.info(
            f'POST REQUEST:\n Ex Dialog:{ex_id} | {json.loads(request.body)}'
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
            another_means = []
            sound_url = None
        else:
            word_text = resp['text']
            word_translation = resp['meanings'][0]['translation']
            transcription = resp['meanings'][0]['transcription']

            for mean in resp['meanings']:
<<<<<<< HEAD
                resp_translation = mean['translation']['text'].lower().replace(
                    'ё', 'е')
                word_translation = word['translate'].lower().replace('ё', 'е')

                if resp_translation == word_translation or \
                        resp_translation in word_translation:
                    # image_url.replace('640x480', img_size)
                    image_url = mean['imageUrl']
                    break
            else:
                image_url = None

            another_means = set([
                mean['translation']['text'].lower().replace('ё', 'е')
                for mean in resp['meanings']
                if mean['translation']['text'].lower().replace('ё', 'е') != word['translate'].lower().replace('ё', 'е')
            ])
            sound_url = resp['meanings'][0]['soundUrl']

=======
                resp_translation = mean['translation']['text'].lower().replace('ё', 'е')
                word_translation = word['translate'].lower().replace('ё', 'е')
                
                if resp_translation == word_translation or \
                    resp_translation in word_translation:
                    image_url = mean['imageUrl'] #image_url.replace('640x480', img_size)
                    break
            else:
                image_url = None
            
            another_means = set([
                mean['translation']['text'].lower().replace('ё', 'е')
                for mean in resp['meanings'] 
                if mean['translation']['text'].lower().replace('ё', 'е') != word['translate'].lower().replace('ё', 'е')
                ])
            sound_url = resp['meanings'][0]['soundUrl']
            
>>>>>>> origin/dev
            logger.info(resp)
        finally:
            result.append(
                {
                    'word': word_text,
                    'translation': word_translation,
                    'transcription': transcription,
                    'image_url': image_url,
                    'another_means': another_means,
                    'sound_url': sound_url
                }
            )

    return result
