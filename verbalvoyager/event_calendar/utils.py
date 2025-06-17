import logging

from django.db import transaction

from event_calendar.models import Lesson, LessonTask

logger = logging.getLogger('django')


def create_tasks(tasks_to_create: dict) -> list:
    if not tasks_to_create:
        return

    students_id = []
    tasks_obj = []

    for task_data in tasks_to_create.values():
        new_task = LessonTask(
            name=task_data['name'],
            points=task_data['points'],
            is_completed=task_data['isCompleted'],
        )

        try:
            new_task.lesson_id = Lesson.objects.get(
                pk=int(task_data['createFor']))
            tasks_obj.append(new_task)

            students_id.append(
                new_task.lesson_id.student_id.id)
        except KeyError as err:
            logger.error(task_data)
            logger.error(err, exc_info=True)

    with transaction.atomic():
        LessonTask.objects.bulk_create(tasks_obj)

    return students_id


def update_tasks(tasks_to_update: dict):
    if not tasks_to_update:
        return

    students_id = []
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

            students_id.append(
                updated_task.lesson_id.student_id.id)

    with transaction.atomic():
        LessonTask.objects.bulk_update(tasks.values(), updated_fields)


def delete_tasks(tasks_to_delete: dict) -> list:
    if not tasks_to_delete:
        return

    students_id = []

    task_objs_to_delete = LessonTask.objects.filter(
        pk__in=tasks_to_delete)

    students_id.extend(
        task_objs_to_delete.values_list(
            'lesson_id__student_id', flat=True
        ).distinct()
    )
    task_objs_to_delete.delete()


def update_lessons(lessons_to_update: dict) -> list:
    students_id = []

    lesson_obj = Lesson.objects.filter(pk__in=lessons_to_update.keys()).all()
    lessons = {lesson.pk: lesson for lesson in lesson_obj}

    for lesson_pk, lesson_status in lessons_to_update.items():
        updated_lesson = lessons.get(int(lesson_pk))

        if updated_lesson:

            if lesson_status.get('performing') is not None:
                updated_lesson.status = lesson_status['performing']
            if lesson_status.get('payment') is not None:
                updated_lesson.is_paid = lesson_status['payment']

            students_id.append(updated_lesson.student_id.id)

    with transaction.atomic():
        Lesson.objects.bulk_update(
            lessons.values(), ('status', 'is_paid',))

    return students_id
