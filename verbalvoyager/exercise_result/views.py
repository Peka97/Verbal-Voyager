import logging
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from .utils import get_exercise_class_name


logger = logging.getLogger('django')


@login_required
def exercise_result_update(request, ex_type, ex_lang, ex_id, step_num=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        logger.info(
            f'POST REQUEST:\n {ex_type}[{ex_id}] ({ex_lang}) | {data}'
        )
        
        exercise_obj, exercise_result_obj = get_exercise_class_name(ex_type, ex_lang)

        if not exercise_obj or not exercise_result_obj:
            return JsonResponse({'error': 'Invalid exercise type'}, status=400)

        with transaction.atomic():
            exercise, _ = exercise_obj.objects.get_or_create(pk=ex_id)
            exercise_result, _ = exercise_result_obj.objects.get_or_create(
                exercise_id=exercise.id,
            )
            
            value = data.get('value')
            
            exercise_result.set_value(step_num, value)

            exercise.save()
            exercise_result.save()

            return JsonResponse({'result': 'Updated'}, status=200)
