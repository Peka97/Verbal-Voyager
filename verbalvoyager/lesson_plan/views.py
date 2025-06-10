import logging
import json

from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch

from .models import EnglishLessonPlan, EnglishLessonMainAims, EnglishLessonSubsidiaryAims
from event_calendar.models import Lesson
from dictionary.models import EnglishWord, Translation

logger = logging.getLogger('django')


def json_update_lesson_plan(request, lesson_id):
    print(lesson_id)
    if request.method == 'POST':
        errors = {}

        # try:
        data = json.loads(request.body)
        print(data)
        lesson_plan_prefetch = (
            Prefetch(
                'new_vocabulary',
                queryset=Translation.objects.all(),
            ),
            Prefetch(
                'main_aims',
                queryset=EnglishLessonMainAims.objects.all(),
            ),
            Prefetch(
                'subsidiary_aims',
                queryset=EnglishLessonSubsidiaryAims.objects.all(),
            )
        )
        prefetched = Prefetch(
            'lesson_plan',
            queryset=EnglishLessonPlan.objects.prefetch_related(
                *lesson_plan_prefetch).all(),
        )

        lesson = Lesson.objects.prefetch_related(
            prefetched).get(pk=lesson_id)

        try:
            lesson_plan = lesson.lesson_plan
        except EnglishLessonPlan.DoesNotExist:
            lesson_plan = EnglishLessonPlan.objects.create(
                lesson_id=lesson)

        with transaction.atomic():
            simple_fields = ['theme', 'materials', 'processes']

            for field in simple_fields:
                if field in data:
                    setattr(lesson_plan, field, data[field])
            lesson_plan.save()

            # Обновляем новые слова (ManyToMany)
            if 'new_vocabulary' in data:
                lesson_plan.new_vocabulary.clear()

                words_qs = Translation.objects.filter(
                    pk__in=data['new_vocabulary']).all()
                if not words_qs:
                    errors[words_qs] = f'Words not found in dictionary.'
                else:
                    lesson_plan.new_vocabulary.set(words_qs)

            if errors:
                return JsonResponse({'message': 'Ошибки обновления слов.', 'errors': errors}, status=400)

            # Обновляем основные цели (ForeignKey)
            if 'main_aims' in data:
                lesson_plan.main_aims.all().delete()

                for aim in data['main_aims']:
                    EnglishLessonMainAims.objects.create(
                        name=aim,
                        lesson_plan_id=lesson_plan
                    )

            # Обновляем подзадачи (ForeignKey)
            if 'subsidiary_aims' in data:
                lesson_plan.subsidiary_aims.all().delete()

                for aim in data['subsidiary_aims']:
                    EnglishLessonSubsidiaryAims.objects.create(
                        name=aim,
                        lesson_plan_id=lesson_plan
                    )

        return JsonResponse({'message': 'Обновлено.'}, status=200)

        # except Lesson.DoesNotExist as e:
        #     logger.error(f'Error updating lesson plan: {e}', exc_info=True)
        #     return JsonResponse({'message': 'План урока не найден.', 'errors': errors}, status=404)
        # except Exception as e:
        #     logger.error(f'Error updating lesson plan: {e}', exc_info=True)
        #     return JsonResponse({'message': 'Что-то пошло не так.', 'errors': errors}, status=500)
