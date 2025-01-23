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

from .models import Word, ExerciseWords, ExerciseDialog, ExerciseResult

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
    popover_data = {
        1: {
            'title': 'Упражнение "Запоминаем"',
            'content': 'Данный шаг рассчитан на твоё знакомство с новым словом.<br>'
            'В первом блоке представлено слово на иностранном языке с <em>транскрипцией</em> под ним и <em>аудио</em> слева.<br>'
            'Ниже поясняющая <em>картинка</em> к слову и <em>примеры с другими значениями</em> данного слова и <em>предложениями</em>, где это слово можно употреблять в качестве примера.<br><br>'
            '<u>Внимательно изучи каждый блок</u>, переключая слова на <em>переключателях</em> в нижней части экрана.'
        },
        2: {
            'title': 'Упражнение "Выбираем"',
            'content': 'Первая проверка того насколько ты хорошо узнал новые слова.<br>'
            'В верхней части написано слово на иностранном языке, а ниже представлены варианты перевода этого слова. Верный из них только один.<br>'
            'Если при нажатии ты увидел, что оно загорелось зеленым, а остальные красным, то всё верно и можешь переходить к следующему слову.<br>'
            'Если же выбранное слово загорелось красным, то ты выбрал не правильно - хорошенько подумай ещё раз и выбери другое слово.<br>'
        },
        3: {
            'title': 'Упражнение "Расставляем"',
            'content': 'Пора поработать со всеми словами сразу.<br>'
            'Слова разделены на два столбика - в первом иностранные, во втором на русском языке. Слова во втором столбике можно менять местами перестакивая (зажми правую кнопку мыши над словом и веди курсор вверх или вниз).<br>'
            'Твоей задачей будет расставить слова так, чтобы напротив каждого был его перевод. Как только захочешь проверить себя, нажми внизу кнопку "Проверить": если всё правильно, то в правом нижнем углу ты увидишь уведомление об успешном прохождении.'
        },
        4: {
            'title': 'Упражнение "Переводим"',
            'content': 'Последний и самый сложный шаг.<br>'
            'Тебе предстоит написать слово на иностранном языке целиком.<br>'
            'В данном упражнении ввод не чувствителен к регистру, а значит можешь написать слово и с маленькой, и с большой буквы (даже если все буквы будут маленькими или большими). Главное - проверить насколько ты хорошо теперь умеешь использовать полученные знания.'
        }
    }
    user = request.user

    exercise = get_object_or_404(ExerciseWords, pk=ex_id, student=user)

    words_obj = list(exercise.words.all())
    words = get_words(words_obj)

    template_name = f'exercises/exercise_step_{step}.html'
    context = {
        'ex_id': ex_id,
        'step': step,
        'title': titles[step],
        'popover': popover_data[step],
        'words': get_words(words_obj),
        'shuffled_translates': get_shuffled_translates(words_obj),
        'len': range(1, len(words) + 1)
    }

    if step == 1:

        if context['words'][0]['lang'] == 'eng':
            api_words = get_api_for_words(words)

            for word, api_word in zip(context['words'], api_words):
                word['api'] = api_word

    return render(request, template_name, context)


@login_required(login_url="/users/auth")
def exercises_dialog(request, ex_id):
    user = request.user

    dialog = get_object_or_404(ExerciseDialog, pk=ex_id, student=user)
    messages = list(filter(lambda s: len(s) > 1, dialog.text.split('\n')))

    scene = messages[0] if messages[0].startswith('Scene:') else None
    text = messages[1:] if scene else messages
    name_1 = text[0][:text[0].index(':')]
    name_2 = text[1][:text[1].index(':')]
    text = [message.removeprefix(f"{name_1}: ").removeprefix(
        f"{name_2}: ") for message in text]
    words = dialog.words.all()

    context = {
        'scene': scene,
        'text': text,
        'words': get_words(words),
        'name_1': name_1,
        'name_2': name_2,
    }
    return render(request, 'exercises/dialog.html', context)


def get_words(words: list[ExerciseWords]):
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
        data = json.loads(request.body)

        logger.info(
            f'POST REQUEST:\n Ex Dialog:{ex_id} | {data}'
        )
        value = data.get('value')

        obj, _ = ExerciseResult.objects.get_or_create(
            words=ExerciseWords.objects.get(pk=ex_id),
        )
        obj.__dict__[step_num] = value
        obj.save()

        if step_num[-1] == '4':
            exercise = ExerciseWords.objects.get(pk=ex_id)
            exercise.is_active = False
            exercise.save()

        return redirect('profile')


@login_required
def exercises_dialog_update(request, ex_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        logger.info(
            f'POST REQUEST:\n Ex Dialog:{ex_id} | {data}'
        )

        value = data.get('value')
        obj, _ = ExerciseResult.objects.get_or_create(
            dialog=ExerciseDialog.objects.get(pk=ex_id),
        )
        obj.__dict__['step_1'] = value
        obj.save()

        dialog = ExerciseDialog.objects.get(pk=ex_id)
        dialog.is_active = False
        dialog.save()

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
            resp = requests.get(url, params, headers=headers)
            resp_json = resp.json()[0]
        except IndexError:
            msg = f"\nWord: {word}.\nResp: {resp.text}."
            logger.exception(msg)

            word_text = word['word']
            word_translation = word['translate']
            transcription = None
            image_url = None
            another_means = []
            sound_url = None
        else:
            word_text = resp_json['text']
            word_translation = resp_json['meanings'][0]['translation']
            transcription = resp_json['meanings'][0]['transcription']

            for mean in resp_json['meanings']:
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
                for mean in resp_json['meanings']
                if mean['translation']['text'].lower().replace('ё', 'е') != word['translate'].lower().replace('ё', 'е')
            ])
            sound_url = resp_json['meanings'][0]['soundUrl']

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


@login_required
def logging(request, ex_id, step_num):
    if request.method == 'POST':
        data = json.loads(request.body)
        is_correct = data.get('is_correct')

        if is_correct != 'wrong':
            logger.info(
                f'Words Correct Check:\n Ex:{ex_id} | Step Num: {step_num} | {data}'
            )
        else:
            logger.error(
                f'Words Correct Check:\n Ex:{ex_id} | Step Num: {step_num} | {data}'
            )

    return HttpResponse({'status': 200})
