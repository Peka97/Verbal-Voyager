import logging
import json

from django.http import JsonResponse
from django.db import transaction

from .models import EnglishLessonPlan, EnglishLessonMainAims, EnglishLessonSubsidiaryAims
from dictionary.models import EnglishWord

logger = logging.getLogger('django')


def json_update_lesson_plan(request, lesson_plan_id):
    if request.method == 'POST':
        errors = {}

        try:
            data = json.loads(request.body)
            lesson_plan = EnglishLessonPlan.objects.prefetch_related(
                'new_vocabulary', 'main_aims', 'subsidiary_aims').get(pk=lesson_plan_id)

            with transaction.atomic():
                simple_fields = ['theme', 'materials', 'processes']

                for field in simple_fields:
                    if field in data:
                        setattr(lesson_plan, field, data[field])
                lesson_plan.save()

                # Обновляем новые слова (ManyToMany)
                if 'new_vocabulary' in data:
                    lesson_plan.new_vocabulary.clear()
                    for word in data['new_vocabulary']:
                        word_obj = EnglishWord.objects.filter(
                            word=word).first()
                        if not word_obj:
                            errors[word] = f'Word "{word}" not found in dictionary.'
                            continue
                        lesson_plan.new_vocabulary.add(word_obj)

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

        except EnglishLessonPlan.DoesNotExist:
            return JsonResponse({'message': 'План урока не найден.', 'errors': errors}, status=404)
        except Exception as e:
            logger.error(f'Error updating lesson plan: {e}', exc_info=True)
            return JsonResponse({'message': 'Что-то пошло не так.', 'errors': errors}, status=500)
