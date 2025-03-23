import json


from django.http import JsonResponse
from django.db import transaction

from logger import get_logger
from .models import Lesson, LessonTask


logger = get_logger()


def filter_lessons_by_student(request, student_id):
    products = Lesson.objects.filter(students=student_id)
    return JsonResponse({x.id: str(x) for x in products})


def update(request):
    data = json.loads(request.body)

    if data.get('tasks'):
        tasks_to_create = data['tasks']['toCreate']
        tasks_to_update = data['tasks']['toUpdate']

        if tasks_to_create:
            for task_data in tasks_to_create.values():
                new_task = LessonTask.objects.create(
                    name=task_data['name'],
                    points=task_data['points'],
                    is_completed=task_data['isCompleted'],
                    lesson_id=Lesson.objects.get(
                        pk=int(task_data['createFor'])),
                )
                new_task.save()

        if tasks_to_update:
            updated_fields = set()

            tasks_obj_to_update = LessonTask.objects.filter(
                pk__in=tasks_to_update.keys()).all()
            tasks = {task.pk: task for task in tasks_obj_to_update}

            for task_pk, task_data in tasks_to_update.items():
                updated_task = tasks.get(int(task_pk))

                if updated_task:
                    if task_data.get('name'):
                        updated_task.name = task_data['name']
                        updated_fields.add('name')
                    if task_data.get('points'):
                        updated_task.points = task_data['points']
                        updated_fields.add('points')
                    if task_data.get('isCompleted'):
                        updated_task.is_completed = task_data['isCompleted']
                        updated_fields.add('is_completed')

            if updated_fields:
                with transaction.atomic():
                    LessonTask.objects.bulk_update(
                        tasks.values(), updated_fields)

    if data.get('lessons'):
        lesson_obj = Lesson.objects.filter(pk__in=data['lessons'].keys()).all()
        lessons = {lesson.pk: lesson for lesson in lesson_obj}

        for lesson_pk, lesson_status in data['lessons'].items():
            updated_lesson = lessons.get(int(lesson_pk))

            if updated_lesson:

                if lesson_status.get('performing') is not None:
                    updated_lesson.status = lesson_status['performing']
                if lesson_status.get('payment') is not None:
                    updated_lesson.is_paid = lesson_status['payment']

        with transaction.atomic():
            Lesson.objects.bulk_update(
                lessons.values(), ('status', 'is_paid',))

    return JsonResponse({'status': 'OK'})
