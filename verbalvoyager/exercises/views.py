import json
import logging
from random import sample, shuffle

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .utils import generate_dialog, get_exercise_or_404

from .models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseRussianWords, \
    ExerciseSpanishWords, ExerciseEnglishDialog, ExerciseFrenchDialog, \
    ExerciseRussianDialog, ExerciseSpanishDialog, ExerciseIrregularEnglishVerb

logger = logging.getLogger('django')
logger_words = logging.getLogger('words')

User = get_user_model()


def exercise_words(request, ex_lang, ex_id, step):
    titles = {1: 'Запоминаем', 2: 'Выбираем',
              3: 'Расставляем', 4: 'По местам!', 5: 'Переводим'}
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
            'title': 'Упражнение "По местам!"',
            'content': 'Набираем обороты.<br>'
            'Слово написано, но буквы перемешаны. Тебе предстоит это исправить.<br>'
            'Хорошо запомни написание слова, тебе это пригодится на следующем шаге.'
        },
        5: {
            'title': 'Упражнение "Переводим"',
            'content': 'Последний и самый сложный шаг.<br>'
            'Тебе предстоит написать слово на иностранном языке целиком.<br>'
            'В данном упражнении ввод не чувствителен к регистру, а значит можешь написать слово и с маленькой, и с большой буквы (даже если все буквы будут маленькими или большими). Главное - проверить насколько ты хорошо теперь умеешь использовать полученные знания.'
        }
    }

    if ex_lang == 'english':
        exercise_obj = ExerciseEnglishWords
    elif ex_lang == 'french':
        exercise_obj = ExerciseFrenchWords
    elif ex_lang == 'russian':
        exercise_obj = ExerciseRussianWords
    elif ex_lang == 'spanish':
        exercise_obj = ExerciseSpanishWords
    else:
        return Http404()

    exercise, redirect = get_exercise_or_404(request, exercise_obj, ex_id)

    if redirect:
        return redirect

    words = exercise.words.all().values()  # type: ignore
    [word.update({'idx': idx + 1}) for idx, word in enumerate(words)]

    if step == 2:
        load_translate_vars(words, ex_lang)

    template_name = f'exercises/{ex_lang}/step_{step}.html'
    context = {
        'ex_lang': ex_lang,
        'ex_id': ex_id,
        'step': step,
        'title': titles[step],
        'popover': popover_data[step],
        'words': words,
        'shuffled_translates': words,
        'words_count_range': range(1, len(words) + 1)
    }

    return render(request, template_name, context)


def exercise_dialog(request, ex_lang, ex_id):
    if ex_lang == 'english':
        exercise_obj = ExerciseEnglishDialog
    elif ex_lang == 'french':
        exercise_obj = ExerciseFrenchDialog
    elif ex_lang == 'russian':
        exercise_obj = ExerciseRussianDialog
    elif ex_lang == 'spanish':
        exercise_obj = ExerciseSpanishDialog
    else:
        return Http404()

    exercise, redirect = get_exercise_or_404(request, exercise_obj, ex_id)

    if redirect:
        return redirect

    raw_dialog = list(filter(lambda s: len(s) > 1,
                      exercise.text.split('\n')))  # type: ignore

    scene = raw_dialog[0] if raw_dialog[0].startswith(
        'Scene:') or raw_dialog[0].startswith('Situation:') else None
    raw_text = raw_dialog[1:] if scene else raw_dialog
    messages = []
    for message in raw_text:
        person_name, message_text = message.split(':', 1)
        messages.append(
            {
                'from': person_name,
                'text': message_text
            }
        )

    words = exercise.words.all().values()  # type: ignore
    [word.update({'idx': idx + 1}) for idx, word in enumerate(words)]

    context = {
        'scene': scene,
        'messages': messages,
        'words': words,
        'lang': ex_lang
    }
    return render(request, f'exercises/dialog.html', context)


# TODO: move to Jinja filter
def load_translate_vars(words: list[dict], ex_lang):
    if ex_lang == 'russian':
        all_translates = [word['word'] for word in words]

        for word in words:
            all_translates_copy = all_translates.copy()
            all_translates_copy.remove(word['word'])

            if len(words) > 4:
                translate_vars = sample(all_translates_copy, 3)
            else:
                translate_vars = sample(all_translates_copy, len(words) - 1)

            translate_vars.append(word['word'])
            shuffle(translate_vars)

            word['translate_vars'] = translate_vars
    else:
        all_translates = [word['translation'] for word in words]

        for word in words:
            all_translates_copy = all_translates.copy()
            all_translates_copy.remove(word['translation'])

            if len(words) > 4:
                translate_vars = sample(all_translates_copy, 3)
            else:
                translate_vars = sample(all_translates_copy, len(words) - 1)

            translate_vars.append(word['translation'])
            shuffle(translate_vars)

            word['translate_vars'] = translate_vars

    return words


def generate_dialog_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as err:
            logger.error(err, exc_info=True)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        words = data.get('words_ids')
        sentences_count = data.get('sentences_count')
        level = data.get('level')
        lang = data.get('lang')
        dialog_text = generate_dialog(
            lang, words, sentences_count, level=level)
        if not dialog_text:
            return JsonResponse({'result': 'Generate fail.'}, status=400)
        dialog_text = dialog_text.replace('**', '')
        return JsonResponse({'result': dialog_text})


def generate_dialog_english_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            words = data.get('words_ids')
            sentences_count = data.get('sentences_count')
            level = data.get('level')
            dialog_text = generate_dialog(
                'английском', words, sentences_count, level=level)
            dialog_text = dialog_text.replace('**', '')
            return JsonResponse({'result': dialog_text})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


def generate_dialog_french_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            words = data.get('words_ids')
            sentences_count = data.get('sentences_count')
            level = data.get('level')
            dialog_text = generate_dialog(
                'французском', words, sentences_count, level=level)
            dialog_text = dialog_text.replace('**', '')
            return JsonResponse({'result': dialog_text})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def words_logging(request, ex_id, step_num):
    if request.method == 'POST':
        data = json.loads(request.body)
        is_correct = data.get('is_correct')

        message = f'Words Correct Check: Ex[{ex_id}] | Step Num: {step_num} | {data}'

        if is_correct != 'wrong':
            logger_words.info(message)
        else:
            logger_words.error(message)

        return HttpResponse({'status': 200})

    return HttpResponse({'status': 400})


def exercise_irregular_verbs(request, ex_id, step):
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

    exercise, redirect = get_exercise_or_404(
        request, ExerciseIrregularEnglishVerb, ex_id)

    if redirect:
        return redirect

    words = exercise.words.select_related(  # type: ignore
        'infinitive').values(
            'id',
            'infinitive__word',
            'past_simple',
            'past_participle',
            'infinitive__translation',
            'infinitive__examples',
            'infinitive__another_means',
            'infinitive__sound_url',
            'infinitive__image_url',
            'infinitive__speech_code',
            'infinitive__definition',
            'infinitive__prefix',
            'infinitive__transcription',
    )

    [word.update({'idx': idx + 1}) for idx, word in enumerate(words)]

    template_name = f'exercises/english/irregular_verbs/step_{step}.html'
    context = {
        'ex_id': ex_id,
        'ex_lang': 'english',
        'step': step,
        'title': titles[step],
        'popover': popover_data[step],
        'words': words,
        'words_count_range': range(1, len(words) + 1)
    }

    return render(request, template_name, context)
