import logging
import json
from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Prefetch


from .utils import create_tasks, update_tasks, delete_tasks, update_lessons
from event_calendar.models import Lesson, LessonTask, Project, ProjectType
from lesson_plan.models import EnglishLessonPlan, EnglishLessonMainAims, EnglishLessonSubsidiaryAims
from dictionary.models import Translation
from users.services.cache import get_cached_lessons_for_teacher, get_cached_lessons_for_other_teacher, get_cached_lessons_for_student


logger = logging.getLogger('django')
User = get_user_model()


def filter_lessons_by_student(request, student_id):
    products = Lesson.objects.filter(students=student_id)
    return JsonResponse({x.id: str(x) for x in products})


def update(request):
    data = json.loads(request.body)
    students_id = []
    tasks_data = data.get('tasks')
    lessons_data = data.get('lessons')

    if tasks_data:
        if tasks_data['toCreate']:
            students_id.extend(create_tasks(tasks_data['toCreate']))
        if tasks_data['toUpdate']:
            students_id.extend(update_tasks(tasks_data['toUpdate']))
        if tasks_data['toDelete']:
            students_id.extend(delete_tasks(tasks_data['toDelete']))

    if lessons_data:
        students_id.extend(update_lessons(lessons_data))

    for student_id in students_id:
        cache.delete_pattern(f"user_{student_id}_lessons*")
        cache.delete_pattern(f"user_{student_id}_lesson_tasks*")

    cache.delete_pattern(f"user_{request.user.pk}_lessons*")
    cache.delete_pattern(f"user_{request.user.pk}_lesson_tasks*")

    return JsonResponse({'status': 'OK'})


def load_teacher_lessons(request, teacher_id):
    context = {}
    teacher_name = ""

    teacher = User.objects.get(pk=teacher_id)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if teacher.username != request.user.username:
        teacher_name = f"{teacher.last_name} {teacher.first_name}"

    lesson_plan_prefetches = (
        Prefetch('new_vocabulary', queryset=Translation.objects.all(),),
        Prefetch('main_aims', queryset=EnglishLessonMainAims.objects.all(),),
        Prefetch('subsidiary_aims',
                 queryset=EnglishLessonSubsidiaryAims.objects.all(),)
    )
    project_types_prefetches = (
        Prefetch('types', queryset=ProjectType.objects.only('name'),),
    )

    prefetches = (
        Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),),
        Prefetch('project_id',
                 queryset=Project.objects.prefetch_related(
                     *project_types_prefetches).all()),
        Prefetch(
            'lesson_plan',
            queryset=EnglishLessonPlan.objects.prefetch_related(
                *lesson_plan_prefetches).all(),
        )
    )
    lesson_fields = (
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id'
    )

    lessons_obj = Lesson.objects.filter(
        teacher_id=teacher.pk,
        datetime__range=(start_date, end_date)) \
        .prefetch_related(*prefetches) \
        .select_related('teacher_id', 'student_id') \
        .only(*lesson_fields) \
        .order_by('datetime')

    # lessons_obj = get_cached_lessons_for_teacher(
    #     request.user, start_date, end_date)

    lessons = defaultdict(list)

    for lesson in lessons_obj:
        lessons[lesson.datetime].append(lesson)

    context['events'] = tuple(lessons.values())
    rendered_template = render(
        request, 'users/account/activities/includes/teacher_events.html', context).content.decode('utf-8')

    return JsonResponse({'status': 'OK', 'html': rendered_template, 'teacher_name': teacher_name})


def load_student_lessons(request, student_id):
    context = {}
    student_name = ""

    student = User.objects.get(pk=student_id)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if student.username != request.user.username:
        student_name = f"{student.last_name} {student.first_name}"

    lesson_plan_prefatches = (
        Prefetch('new_vocabulary', queryset=Translation.objects.all(),),
        Prefetch('main_aims', queryset=EnglishLessonMainAims.objects.all(),),
        Prefetch('subsidiary_aims',
                 queryset=EnglishLessonSubsidiaryAims.objects.all(),)
    )
    project_types_prefatches = (
        Prefetch('types', queryset=ProjectType.objects.only('name'),),
    )

    prefatches = (
        Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),),
        Prefetch('project_id',
                 queryset=Project.objects.prefetch_related(
                     *project_types_prefatches).all()),
        Prefetch(
            'lesson_plan',
            queryset=EnglishLessonPlan.objects.prefetch_related(
                *lesson_plan_prefatches).all(),
        )
    )
    lesson_fields = (
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id'
    )
    lessons = Lesson.objects.filter(
        student_id=student.pk,
        datetime__range=(start_date, end_date)
    ).prefetch_related(
        *prefatches
    ).select_related(
        'teacher_id', 'student_id'
    ).only(*lesson_fields).order_by('datetime')

    # lessons = get_cached_lessons_for_student(
    #     request.user, start_date, end_date)

    context['events'] = lessons
    rendered_template = render(
        request, 'users/account/activities/includes/student_events.html', context).content.decode('utf-8')

    return JsonResponse({'status': 'OK', 'html': rendered_template, 'student_name': student_name})


def load_another_teacher_lessons(request, teacher_id):
    context = {}
    teacher_name = ""

    teacher = User.objects.get(pk=teacher_id)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if teacher.username != request.user.username:
        teacher_name = f"{teacher.last_name} {teacher.first_name}"

    lessons_obj = get_cached_lessons_for_other_teacher(
        request.user, teacher.id, start_date, end_date)

    lessons = defaultdict(list)

    for lesson in lessons_obj:
        lessons[lesson.datetime].append(lesson)

    context['events'] = tuple(lessons.values())
    rendered_template = render(
        request, 'users/account/activities/includes/teacher_events.html', context).content.decode('utf-8')

    return JsonResponse({'status': 'OK', 'html': rendered_template, 'teacher_name': teacher_name})

# TODO: рефактор под StreamingHttpResponse?
# def load_teacher_lessons(request, teacher_id):
#     context = {}
#     teacher_name = ""

#     teacher = User.objects.get(pk=teacher_id)

#     if teacher.username != request.user.username:
#         teacher_name = f"{teacher.last_name} {teacher.first_name}"

#     lessons_obj = get_cached_lessons_for_other_teacher(
#         request.user, teacher.id)

#     lessons = defaultdict(list)

#     for lesson in lessons_obj:
#         lessons[lesson.datetime].append(lesson)

#     context['events'] = tuple(lessons.values())
#     rendered_template = render(
#         request, 'users/account/activities/includes/teacher_events.html', context).content.decode('utf-8')

#     return JsonResponse({'status': 'OK', 'html': rendered_template, 'teacher_name': teacher_name})
