import json
from pprint import pprint

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from logger import get_logger
from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb
from exercise_result.models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult, ExerciseEnglishDialogResult, ExerciseFrenchDialogResult, ExerciseIrregularEnglishVerbResult


logger = get_logger()


@login_required
def exercise_result_update(request, ex_type, ex_lang, ex_id, step_num=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        logger.info(
            f'POST REQUEST:\n {ex_type}[{ex_id}] ({ex_lang}) | {data}'
        )
        pprint(data)

        value = data.get('value')

        if ex_type == 'words':
            if ex_lang == 'english':
                exercise_obj = ExerciseEnglishWords
                exercise_result_obj = ExerciseEnglishWordsResult
            elif ex_lang == 'french':
                exercise_obj = ExerciseFrenchWords
                exercise_result_obj = ExerciseFrenchWordsResult
        elif ex_type == 'dialog':
            if ex_lang == 'english':
                exercise_obj = ExerciseEnglishDialog
                exercise_result_obj = ExerciseEnglishDialogResult
            elif ex_lang == 'french':
                exercise_obj = ExerciseFrenchDialog
                exercise_result_obj = ExerciseFrenchDialogResult
        elif ex_type == 'irregular_verbs':
            exercise_obj = ExerciseIrregularEnglishVerb
            exercise_result_obj = ExerciseIrregularEnglishVerbResult
        else:
            return JsonResponse({'error': 'Invalid exercise type'}, status=400)

        with transaction.atomic():
            exercise, _ = exercise_obj.objects.get_or_create(pk=ex_id)
            exercise_result, _ = exercise_result_obj.objects.get_or_create(
                exercise_id=exercise,
            )

            if ex_type == 'words':
                exercise_result.__dict__[step_num] = value

                if step_num and step_num[-1] == '4':
                    exercise.is_active = False

            elif ex_type == 'dialog':
                exercise_result.points = value
                exercise.is_active = False

            elif ex_type == 'irregular_verbs':
                exercise_result.__dict__[step_num] = value

                if step_num and step_num[-1] == '3':
                    exercise.is_active = False

            exercise.save()
            exercise_result.save()

            return JsonResponse({'result': 'Updated'}, status=200)


@login_required
def exercise_result_words_english_update(request, ex_id, step_num):
    if request.method == 'POST':
        with transaction.atomic():
            data = json.loads(request.body)

            logger.info(
                f'POST REQUEST:\n Ex Words:{ex_id} | {data}'
            )
            value = data.get('value')

            exercise = ExerciseEnglishWords.objects.get(pk=ex_id)
            exercise_result, _ = ExerciseEnglishWordsResult.objects.get_or_create(
                words=exercise,
            )
            exercise_result.__dict__[step_num] = value
            exercise_result.save()

            if step_num[-1] == '4':
                exercise.is_active = False
                exercise.save()

        return redirect('profile')


@login_required
def exercise_result_words_french_update(request, ex_id, step_num):
    if request.method == 'POST':
        with transaction.atomic():
            data = json.loads(request.body)

            logger.info(
                f'POST REQUEST:\n Ex Words:{ex_id} | {data}'
            )
            value = data.get('value')

            exercise = ExerciseFrenchWords.objects.get(pk=ex_id)
            exercise_result, _ = ExerciseFrenchWordsResult.objects.get_or_create(
                words=exercise,
            )
            exercise_result.__dict__[step_num] = value
            exercise_result.save()

            if step_num[-1] == '4':
                exercise.is_active = False
                exercise.save()

        return redirect('profile')


@login_required
def exercise_result_dialog_english_update(request, ex_id):
    if request.method == 'POST':
        with transaction.atomic():
            data = json.loads(request.body)

            logger.info(
                f'POST REQUEST:\n Ex Dialog:{ex_id} | {data}'
            )

            value = data.get('value')

            dialog = ExerciseEnglishDialog.objects.get(pk=ex_id)
            exercise_result, _ = ExerciseEnglishDialogResult.objects.get_or_create(
                dialog=dialog,
            )
            exercise_result.points = value
            exercise_result.save()

            dialog.is_active = False
            dialog.save()

        return redirect('profile')


@login_required
def exercise_result_dialog_french_update(request, ex_id):
    if request.method == 'POST':
        with transaction.atomic():
            data = json.loads(request.body)

            logger.info(
                f'POST REQUEST:\n Ex Dialog:{ex_id} | {data}'
            )

            value = data.get('value')

            dialog = ExerciseFrenchDialog.objects.get(pk=ex_id)
            exercise_result, _ = ExerciseFrenchDialogResult.objects.get_or_create(
                dialog=dialog,
            )
            exercise_result.points = value
            exercise_result.save()

            dialog.is_active = False
            dialog.save()

        return redirect('profile')

# TODO: add result for IrregularVerbs
