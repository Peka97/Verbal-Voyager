import json
import logging
from random import sample, shuffle

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from dictionary.models import Language, Translation, Word

from .models import ExerciseDialog, ExerciseIrregularEnglishVerb, ExerciseWords
from .utils import check_exercise_access, new_generate_dialog


logger = logging.getLogger('django')
logger_words = logging.getLogger('words')

User = get_user_model()


# TODO: move to Jinja filter
# def load_translate_vars(words: list[dict], ex_lang):
#     if ex_lang == 'russian':
#         all_translates = [word['word'] for word in words]

#         for word in words:
#             all_translates_copy = all_translates.copy()
#             all_translates_copy.remove(word['word'])

#             if len(words) > 4:
#                 translate_vars = sample(all_translates_copy, 3)
#             else:
#                 translate_vars = sample(all_translates_copy, len(words) - 1)

#             translate_vars.append(word['word'])
#             shuffle(translate_vars)

#             word['translate_vars'] = translate_vars
#     else:
#         all_translates = [word['translation'] for word in words]

#         for word in words:
#             all_translates_copy = all_translates.copy()
#             all_translates_copy.remove(word['translation'])

#             if len(words) > 4:
#                 translate_vars = sample(all_translates_copy, 3)
#             else:
#                 translate_vars = sample(all_translates_copy, len(words) - 1)

#             translate_vars.append(word['translation'])
#             shuffle(translate_vars)

#             word['translate_vars'] = translate_vars

#     return words


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


def new_exercise_words(request, ex_id, step):
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
            'Слова разделены на два столбика - в первом иностранные, во втором на русском языке. Слова во втором столбике можно менять местами перетаскивая (зажми правую кнопку мыши над словом и веди курсор вверх или вниз).<br>'
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

    exercise_qs = ExerciseWords.objects.select_related('lang').filter(pk=ex_id)

    if not exercise_qs.exists():
        return HttpResponse({'status': 404})

    exercise = exercise_qs.first()
    _, redirect = check_exercise_access(request, exercise)

    if redirect:
        return redirect

    words_prefetch_qs = Word.objects.select_related('language')

    if step == 1:
        source_word_prefetch_qs = words_prefetch_qs.prefetch_details(
            exercise.lang.name)
        target_word_prefetch_qs = words_prefetch_qs
    else:
        source_word_prefetch_qs = words_prefetch_qs
        target_word_prefetch_qs = words_prefetch_qs

    translations_prefetched = [
        Prefetch('source_word', queryset=source_word_prefetch_qs),
        Prefetch('target_word', queryset=target_word_prefetch_qs),
    ]

    translations_qs = exercise.words.prefetch_related(
        *translations_prefetched).all()

    template_name = f'exercises/words/step_{step}.html'
    context = {
        'ex_lang': exercise.lang.name,
        'ex_id': ex_id,
        'exercise': exercise,
        'step': step,
        'title': titles[step],
        'popover': popover_data[step],
        'translations': translations_qs.all(),
        'words_count_range': range(1, translations_qs.count() + 1)
    }

    return render(request, template_name, context)


def new_exercise_dialog(request, ex_id):
    exercise = ExerciseDialog.objects.select_related('lang').get(pk=ex_id)
    _, redirect = check_exercise_access(request, exercise)

    if redirect:
        return redirect

    words_prefetch_qs = Word.objects.select_related('language')

    translations_prefetched = [
        Prefetch('source_word', queryset=words_prefetch_qs),
        Prefetch('target_word', queryset=words_prefetch_qs),
    ]

    translations_qs = exercise.words.prefetch_related(
        *translations_prefetched).all()

    raw_dialog = tuple(
        filter(lambda s: len(s) > 1, exercise.text.split('\n'))
    )  # type: ignore

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

    context = {
        'scene': scene,
        'messages': messages,
        'translations': translations_qs.all(),
        'lang': exercise.lang.name
    }
    return render(request, 'exercises/dialogs/dialog.html', context)


def new_exercise_irregular_verbs(request, ex_id, step):
    titles = {1: 'Запоминаем', 2: 'Выбираем',
              3: 'Выбираем (сложно)'}
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
            'content': 'Первая проверка того насколько ты хорошо узнал новые формы неправильных глаголов.<br>'
            'Перед тобой три формы глагола в плитках, но одна из них пропала. Твоей задачей будет выбрать подходящую форму.<br>'
            'Если при нажатии ты увидел, что плитка загорелась зеленым, то всё верно и можешь переходить к следующему слову.<br>'
            'Если же выбранное слово загорелось красным, то ты выбрал не правильно - хорошенько подумай ещё раз и выбери другое слово.<br>'
        },
        3: {
            'title': 'Упражнение "Расставляем"',
            'content': 'Пора поработать с двумя неизвестными формами сразу.<br>'
            'Задача та же, что и в прошлом шаге, но теперь известна только одна форма. По ней ты должен понять и подставить остальные формы.<br>'
            'Если при нажатии ты увидел, что плитка загорелась зеленым, то всё верно и можешь переходить к следующему слову.<br>'
            'Если же выбранное слово загорелось красным, то ты выбрал не правильно - хорошенько подумай ещё раз и выбери другое слово.<br>'
        },
    }

    exercise = ExerciseIrregularEnglishVerb.objects.get(pk=ex_id)
    _, redirect = check_exercise_access(request, exercise)

    if redirect:
        return redirect

    words_prefetch_qs = Word.objects.select_related('language')

    if step == 1:
        source_word_prefetch_qs = words_prefetch_qs.prefetch_details('English')
        target_word_prefetch_qs = words_prefetch_qs
    else:
        source_word_prefetch_qs = words_prefetch_qs
        target_word_prefetch_qs = words_prefetch_qs

    translations_prefetched = [
        Prefetch('source_word', queryset=source_word_prefetch_qs),
        Prefetch('target_word', queryset=target_word_prefetch_qs),
    ]

    translations_qs = Prefetch(
        'translations_from',
        queryset=Translation.objects.prefetch_related(
            *translations_prefetched),
        to_attr='prefetched_translations_from'
    )

    prefetched = Prefetch(
        'infinitive',
        queryset=Word.objects.prefetch_related(translations_qs)
    )

    irregular_verbs = exercise.words.prefetch_related(prefetched).all()

    template_name = f'exercises/irregular_verbs/step_{step}.html'
    context = {
        'title': titles[step],
        'popover': popover_data[step],
        'ex_id': ex_id,
        'ex_lang': 'english',
        'step': step,
        'irregular_verbs': irregular_verbs,
        'words_count_range': range(1, len(irregular_verbs) + 1)
    }

    return render(request, template_name, context)


def new_generate_dialog_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            words = data.get('words_ids')
            sentences_count = data.get('sentences_count')
            level = data.get('level')
            lang = data.get('langID')
            language = Language.objects.get(pk=lang).name
            dialog_text = new_generate_dialog(
                language, words, sentences_count, level=level)
            dialog_text = dialog_text.replace('**', '')
            return JsonResponse({'result': dialog_text})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
