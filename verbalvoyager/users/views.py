from collections import defaultdict
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
from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseDialog
from event_calendar.models import Lesson, Project, Course
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
    context = {
        'form': RegistrationUserForm(),
        'auth_show': True
    }

    next = request.GET.get('next')

    if request.POST:

        # Регистрация
        if request.POST.get('username'):
            form = RegistrationUserForm(request.POST)

            if form.is_valid():
                user = form.save(commit=False)
                user.save()

                login(request, user)
                return redirect('')
            else:
                context['form'] = form
                context['auth_show'] = False

        # Авторизация
        elif request.POST.get('login'):
            username = request.POST.get('login')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect(next) if next else redirect('')
            else:
                context['auth_error'] = 'Неправильное имя пользователя или пароль'

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
    context = {
        'user_is_teacher': user.is_teacher()
    }

    if context['user_is_teacher']:
        projects = Project.objects.filter(
            teacher_id=user).values_list('pk', flat=True).all()
        lessons_obj = Lesson.objects.filter(
            teacher_id=user
        ).prefetch_related('lesson_tasks').select_related('teacher_id', 'student_id').order_by('datetime').all()
        lessons = defaultdict(list)

        for lesson in lessons_obj:
            lessons[lesson.datetime].append(lesson)

        lessons = tuple(lessons.values())
    else:
        lessons = Lesson.objects.filter(
            student_id=user
        ).prefetch_related('lesson_tasks').select_related('teacher_id', 'student_id').order_by('datetime').all()

        projects = Project.objects.filter(
            students=user).values_list('pk', flat=True).all()
        # lessons = Lesson.objects.filter(
        #     project_id__in=tuple(projects),
        #     student_id=user,
        #     ).prefetch_related('lesson_tasks').select_related('teacher_id', 'student_id').order_by('datetime').all()
        context['projects'] = projects
        context['exercises_eng'] = ExerciseEnglishWords.objects.filter(
            student=user.pk,
            is_active=True
        ).all()
        context['exercises_fr'] = ExerciseFrenchWords.objects.filter(
            student=user.pk,
            is_active=True
        ).all()
        context['dialogs'] = ExerciseDialog.objects.filter(
            student=user.pk,
            is_active=True
        ).all()

    context['events'] = lessons
    # print(tuple(lessons)[0].lesson_tasks)
    # print(lessons.values()[0])
    # context['new_events'] = lessons_new
    # context['events_count_total'] = len(lessons)
    # context['events_count_done'] = lessons.filter(status='D').count()
    context['courses'] = tuple(Course.objects.all())

    return render(request, 'users/profile.html', context)


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
