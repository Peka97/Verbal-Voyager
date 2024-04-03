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

from .models import Exercise, Word, ExerciseResult

logger = logging.getLogger(__file__)
User = get_user_model()


@login_required
def exercises_words(request, id, step):
    titles = {1: 'Запоминаем', 2: 'Выбираем', 3: 'Расставляем', 4: 'Переводим'}
    user = User.objects.get(username=request.user.username)

    try:
        exercise = list(Exercise.objects.filter(
            id=id,
            student=user
        ).all())[0]
    except IndexError:
        raise PermissionDenied

    words = get_words(exercise)

    template_name = f'exercises/exercise_step_{step}.html'
    context = {
        'id': id,
        'step': step,
        'title': titles[step],
        'words': words,
        'shuffled_translates': get_shuffled_translates(list(exercise.words.all())),
        'len': range(1, len(words) + 1)
    }

    if step == '1' or step == 1:
        api_words = get_api_for_words(words)

        for word, api_word in zip(context['words'], api_words):
            word['api'] = api_word

    return render(request, template_name, context)


def get_words(exercise: list[Exercise]):  # list[Exercise]
    result = []
    words = list(exercise.words.all())

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
def update(request, id):
    if request.method == 'POST':
        # data = json.loads(request.body)
        # exercise_id = data.get('exercise_id')
        # step = data.get('step')
        # value = data.get('value')
        # obj, is_created = ExerciseResult.objects.get_or_create(
        #     exercise=Exercise.objects.get(pk=exercise_id),
        #     step=step,
        #     result=value
        # )

        # if is_created:
        #     try:
        #         obj.save()
        #     except Exception:
        #         print('Ошибка добавления')

        exercise = Exercise.objects.get(pk=id)
        exercise.is_active = False
        exercise.save()

        return redirect('profile')

    return HttpResponse('Not POST method')


def get_api_for_words(words: list[Word]):
    img_size = '300x300'
    result = []

    url = 'https://dictionary.skyeng.ru/api/public/v1/words/search?search=stone'
    headers = {'accept': 'application/json'}
    params = {'search': ''}

    for word in words:
        params['search'] = word['word']
        resp = requests.get(url, params, headers=headers).json()[0]

        word = resp['text']
        translation = resp['meanings'][0]['translation']
        transcription = resp['meanings'][0]['transcription']
        image_url = resp['meanings'][0]['imageUrl']
        image_url = image_url.replace('640x480', img_size)
        sound_url = resp['meanings'][0]['soundUrl']

        result.append(
            {
                'word': word,
                'translation': translation,
                'transcription': transcription,
                'image_url': image_url,
                'sound_url': sound_url
            }
        )

    return result
