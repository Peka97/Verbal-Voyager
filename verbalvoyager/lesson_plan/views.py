import logging
import json

from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch

from exercises.models import ExerciseCategory, ExerciseWords

from .models import EnglishLessonPlan, EnglishLessonMainAims, EnglishLessonSubsidiaryAims
from event_calendar.models import Lesson
from dictionary.models import Language, Translation

logger = logging.getLogger('django')


def json_update_lesson_plan(request, lesson_id):
    if request.method == 'POST':
        errors = []

        # try:
        data = json.loads(request.body)
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

            if 'new_vocabulary' in data:
                lesson_plan.new_vocabulary.clear()

                words = Translation.objects.filter(
                    pk__in=data['new_vocabulary']).all()
                if not words:
                    for word in data['new_vocabulary']:
                        errors.append(f'Word "{word}"not found in dictionary.')
                else:
                    lesson_plan.new_vocabulary.set(words)

                if lesson_plan.exercise_id:
                    lesson_plan.exercise_id.words.set(words)
                else:
                    category, _ = ExerciseCategory.objects.get_or_create(
                        name='New vocabulary')
                    exercise = ExerciseWords(
                        name='New vocabulary',
                        category=category,
                        student=lesson_plan.lesson_id.student_id,
                        teacher=lesson_plan.lesson_id.teacher_id,
                        lang=Language.objects.get(name='English'),
                    )

                    exercise.save()
                    exercise.words.set(words)

                    lesson_plan.exercise_id = exercise
                    lesson_plan.save()

            if errors:
                return JsonResponse({'message': 'Ошибки обновления слов.', 'errors': errors}, status=400)

            if 'main_aims' in data:
                lesson_plan.main_aims.all().delete()

                for aim in data['main_aims']:
                    EnglishLessonMainAims.objects.create(
                        name=aim,
                        lesson_plan_id=lesson_plan
                    )

            if 'subsidiary_aims' in data:
                lesson_plan.subsidiary_aims.all().delete()

                for aim in data['subsidiary_aims']:
                    EnglishLessonSubsidiaryAims.objects.create(
                        name=aim,
                        lesson_plan_id=lesson_plan
                    )

        return JsonResponse({'message': 'Обновлено.'}, status=200)
