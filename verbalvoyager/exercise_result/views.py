import logging
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from .utils import get_exercise_and_result_class, get_last_step


logger = logging.getLogger('django')


@login_required
def exercise_result_update(request, ex_type, ex_id, step_num=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        exercise_obj, exercise_result_obj = get_exercise_and_result_class(
            ex_type)
        if not exercise_obj or not exercise_result_obj:
            return JsonResponse({'error': 'Invalid exercise type.'}, status=400)

        with transaction.atomic():
            exercise_qs = exercise_obj.objects.filter(pk=ex_id)

            if not exercise_qs.exists():
                return JsonResponse({'error': 'Exercise not found.'}, status=404)

            exercise = exercise_qs.first()
            if request.user != exercise.student:
                return JsonResponse({'error': 'Exercise not for this student.'}, status=401)

            exercise_result, _ = exercise_result_obj.objects.get_or_create(
                exercise=exercise,
            )

            value = data.get('value')

            if hasattr(exercise_result, 'points'):
                exercise_result.points = value
            else:
                exercise_result.set_value(step_num, value)

            exercise_result.save()

            last_step = get_last_step(ex_type)

            if step_num == last_step:
                exercise.is_active = False
                exercise.save()

        return JsonResponse({'result': 'Updated.'}, status=200)
