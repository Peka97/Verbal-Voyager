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

from users.forms import RegistrationUserForm, CustomPasswordResetForm
from exercises.models import ExerciseWords, ExerciseDialog
from event_calendar.models import Lesson, Project
from event_calendar.forms import LessonForm
from verbalvoyager.settings import DEBUG_LOGGING_FP

log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(DEBUG_LOGGING_FP)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

User = get_user_model()


def user_auth(request, **kwargs):
    context = {}

    next = request.GET.get('next')

    if request.POST:
        username = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and next:
            login(request, user)
            return redirect(next)
        elif user:
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


@login_required(login_url="/users/auth")
def user_profile(request):
    user = request.user

    if user.is_teacher():
        context = {
            'user_is_teacher': True,
        }
        lessons = list(Lesson.objects.filter(teacher=user.pk).order_by(
            'datetime').all().prefetch_related('students'))
        calendar = get_calendar(lessons)

        # Форма отключена за ненадобностью
        # lesson_form = LessonForm()
        # lesson_form.fields['teacher'].initial = user
        # context['lesson_form'] = lesson_form

        context['events'] = lessons
        context['events_count_total'] = len(lessons)
        context['calendar'] = calendar

        return render(request, 'users/profile.html', context)
    else:
        context = {
            'user_is_teacher': False,
        }
        exercises = list(ExerciseWords.objects.filter(
            student=user.pk,
            is_active=True
        ).all())
        dialogs = list(ExerciseDialog.objects.filter(
            student=user.pk,
            is_active=True
        ).all())
        lessons = list(Lesson.objects.filter(
            students=user).order_by('datetime').select_related('teacher').all()
        )
        calendar = get_calendar(lessons)
        projects = get_projects(user)

        context['projects'] = projects
        context['exercises'] = exercises
        context['dialogs'] = dialogs
        context['events'] = lessons
        context['events_count_total'] = len(lessons)
        context['events_count_done'] = len(
            [lesson for lesson in lessons if lesson.status == 'D'])
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


def get_projects(user: User):
    projects = Project.objects.filter(students=user).all()
    return projects if projects else None


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    from_email = 'verbal-voyager@gmail.com'
    extra_email_context = {
        'site_name': 'Verbal Voyager',
        'domain': 'verbal-voyager.ru',
        'protocol': 'https'
    }


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    form_class = PasswordResetCompleteView
    template_name = 'users/password_reset_form.html'
    success_url = ''
