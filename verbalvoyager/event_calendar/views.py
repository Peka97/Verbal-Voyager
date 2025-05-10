from encodings.punycode import T
import logging
import json
from collections import defaultdict

from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.core.cache import cache

from .models import Lesson, LessonTask
from event_calendar.models import Lesson, LessonTask, Project, Course, ProjectType


logger = logging.getLogger('django')
User = get_user_model()


def filter_lessons_by_student(request, student_id):
    products = Lesson.objects.filter(students=student_id)
    return JsonResponse({x.id: str(x) for x in products})


def update(request):
    data = json.loads(request.body)
    students_id_to_clear_cache = []

    if data.get('tasks'):
        tasks_to_create = data['tasks']['toCreate']
        tasks_to_update = data['tasks']['toUpdate']
        tasks_to_delete = data['tasks']['toDelete']

        if tasks_to_create:
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
                    students_id_to_clear_cache.append(new_task.lesson_id.student_id.id)
                except KeyError as err:
                    logger.error(task_data)
                    logger.error(err, exc_info=True)

            with transaction.atomic():
                LessonTask.objects.bulk_create(tasks_obj)

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
                    
                    students_id_to_clear_cache.append(updated_task.lesson_id.student_id.id)

            with transaction.atomic():
                LessonTask.objects.bulk_update(
                    tasks.values(), updated_fields)

        if tasks_to_delete:
            task_objs_to_delete = LessonTask.objects.filter(pk__in=tasks_to_delete)
            students_id_to_clear_cache.extend(
                task_objs_to_delete.values_list(
                    'lesson_id__student_id', flat=True
                ).distinct()
            )
            task_objs_to_delete.delete()

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
                
                students_id_to_clear_cache.append(updated_lesson.student_id.id)

        with transaction.atomic():
            Lesson.objects.bulk_update(
                lessons.values(), ('status', 'is_paid',))
    
    cache.delete_pattern(f"user_{request.user.id}_lessons*")
    cache.delete_pattern(f"user_{request.user.id}_lesson_tasks*")
    for student_id in students_id_to_clear_cache:
        print(student_id)
        cache.delete_pattern(f"user_{student_id}_lessons*")
        cache.delete_pattern(f"user_{student_id}_lesson_tasks*")

    return JsonResponse({'status': 'OK'})


# TODO: рефактор под StreamingHttpResponse
def load_teacher_lessons(request, teacher_id):
    context = {}

    teacher = User.objects.get(pk=teacher_id)
    teacher_name = f"{teacher.last_name} {teacher.first_name}"

    project_types_prefetch = Prefetch(
        'types',
        queryset=ProjectType.objects.only('name'),
        to_attr='prefetched_types'
    )
    projects_prefetch = Prefetch(
        'project_id',
        queryset=Project.objects.only('id'
        ).prefetch_related(project_types_prefetch),
        to_attr='prefetched_project'
    )
    
    lessons_obj = Lesson.objects.filter(
        teacher_id=teacher_id
    ).prefetch_related(
        'lesson_tasks',
        projects_prefetch
    ).select_related('teacher_id', 'student_id', 'project_id'
    ).order_by('datetime').only(
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status', 
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id',
    ).all()
    lessons = defaultdict(list)

    for lesson in lessons_obj:
        lessons[lesson.datetime].append(lesson)

    lessons = tuple(lessons.values())

    context['events'] = lessons
    rendered_template = render(
        request, 'users/account/activities/includes/teacher_events.html', context).content.decode('utf-8')

    return JsonResponse({'status': 'OK', 'html': rendered_template, 'teacher_name': teacher_name})
