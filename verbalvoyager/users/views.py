import logging
from datetime import datetime
from calendar import monthrange
from pprint import pprint

import pytz
from typing import Any, Dict

from django.shortcuts import render, HttpResponse
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView

from pages.models import Project
from exercises.models import Exercise
from users.forms import RegistrationUserForm, CustomPasswordResetForm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(
    '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
)

User = get_user_model()


def user_auth(request, **kwargs):
    context = {}

    if request.POST:
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('')
        else:
            context = {'error': 'Неправильный логин или пароль'}

    return render(request, 'users/auth.html', context)


def user_sign_up(request):
    context = {}
    if request.method == 'GET':
        form = RegistrationUserForm()

    if request.method == 'POST':
        form = RegistrationUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('')

    context['form'] = form

    return render(request, 'users/sign_up.html', context)


def user_logout(request):
    logout(request)
    return redirect('')


@login_required
def user_profile(request):
    context = {}

    # if request.method == 'POST':
    #     print(request.POST)

    user = User.objects.get(username=request.user.username)

    if user.is_teacher():
        lessons = []  # get_teacher_lessons(user)
        calendar = get_calendar(lessons)
        # lesson_form = LessonForm()
        # lesson_form.fields['teacher'].initial = user

        context = {
            'events': lessons,
            'events_count_total': len(lessons),
            'calendar': calendar,
            'user_is_teacher': True,
            'lesson_form':  None  # lesson_form
        }
        return render(request, 'users/profile.html', context)
    else:
        exercises = list(Exercise.objects.filter(
            student=user,
            is_active=True
        ).all())
        # lessons = list(Lesson.objects.filter(
        #     students=user_login).order_by('datetime').all()
        # )
        lessons = []
        calendar = get_calendar(lessons)
        # projects = get_projects(user)

        context['projects'] = []  # projects
        context['exercises'] = exercises
        context['events'] = []  # lessons
        context['events_count_total'] = 0  # len(lessons)
        context['events_count_done'] = 0
        # context['events_count_done'] =  len([lesson for lesson in lessons if lesson.status == 'D'])
        context['calendar'] = calendar

        return render(request, 'users/profile.html', context)


def get_calendar(lessons: list[dict], tzname='Europe/Saratov'):
    current_cell = 0
    day_idx = 0

    result = '<tr class="table-row"></tr>'
    today = datetime.now(pytz.timezone(tzname))
    weekday_start_month = datetime(today.year, today.month, 1).weekday()
    days = monthrange(today.year, today.month)
    days_range = range(days[0], days[1] + 1)

    result += '<tr class="table-row"></tr>'

    for _ in range(weekday_start_month):
        result += '<td class="table-date nil"></td>'
        current_cell += 1

    while True:
        if current_cell == 7:
            current_cell = 0
            result += '</tr><tr class="table-row">'

        try:
            current_day = days_range[day_idx]
        except IndexError:
            result += '</tr>'
            break

        class_name = 'table-date'

        if current_day == today.day:
            class_name += ' active-date'

        for lesson in lessons:
            if isinstance(lesson, dict):
                if lesson['datetime'].day == current_day:
                    class_name += ' event-date'
            else:
                if lesson.datetime.day == current_day:
                    class_name += ' event-date'

        result += f'<td class="{class_name}">{current_day}</td>'

        current_cell += 1
        day_idx += 1

    return result


# def get_teacher_lessons(user: User):
#     lessons = []
#     lesson_template = {
#         'pk': 0,
#         'type': 'personal',  # personal / group,
#         'title': 'English',  # English / French / Spanish
#         'datetime': None,
#         'lessons': Lesson  # Lesson / list[Lesson]
#     }

#     events_filter = Lesson.objects.filter(
#         teacher=user).all().order_by('datetime')
#     events = [
#         Lesson.objects.get(pk=event.pk)
#         for event in events_filter
#     ]

#     return events

    # for event in events:
    #     events_datetime = [lesson['datetime'] for lesson in lessons]

    #     if event.datetime in events_datetime:
    #         event_idx = events_datetime.index(event.datetime)
    #         lesson_info = lessons[event_idx]
    #         lesson_info['type'] = 'group'
    #         if isinstance(lesson_info['lessons'], list):
    #             lesson_info['lessons'].append(event)
    #         else:
    #             lesson_info['lessons'] = [
    #                 lesson_info['lessons'], event
    #             ]
    #     else:
    #         lesson_info = lesson_template.copy()
    #         lesson_info['pk'] = event.pk
    #         lesson_info['title'] = event.title
    #         lesson_info['datetime'] = event.datetime
    #         lesson_info['lessons'] = event
    #         lessons.append(lesson_info)

    # lessons.sort(key=lambda x: x['datetime'])
    # return lessons


def get_projects(user: User):
    projects = Project.objects.filter(student=user).all()
    return projects if projects else None


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset_form.html'
    success_url = ''


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    form_class = PasswordResetCompleteView
    template_name = 'users/password_reset_form.html'
    success_url = ''