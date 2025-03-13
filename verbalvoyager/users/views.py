from collections import defaultdict
import logging
from datetime import datetime
from calendar import monthrange
from pprint import pprint
from itertools import chain

import pytz
from typing import Any, Dict

from django.shortcuts import render, HttpResponse
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView

from logger import get_logger
from users.forms import RegistrationUserForm, CustomPasswordResetForm
from users.utils import get_words_learned_count, get_exercises_done_count
from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb
from event_calendar.models import Lesson, Project, Course


logger = get_logger()
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
def user_account(request, current_pane):
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
        ).prefetch_related('lesson_tasks', 'project_id__types').select_related('teacher_id', 'student_id', 'project_id',).order_by('datetime').all()

        projects = Project.objects.filter(
            students=user).values_list('pk', flat=True).all()
        context['projects'] = projects
        english_words, french_words = ExerciseEnglishWords.objects.filter(student=user.pk), \
            ExerciseFrenchWords.objects.filter(student=user.pk)
        context['exercises_words'] = tuple(chain(
            english_words.all(),
            french_words.all()
        ))
        irregular_verbs = ExerciseIrregularEnglishVerb.objects.filter(
            student=user.pk)

        context['exercises_irregular_verbs'] = irregular_verbs.filter(
            is_active=True).all()
        english_dialogs, french_dialogs = ExerciseEnglishDialog.objects.filter(
            student=user.pk), ExerciseFrenchDialog.objects.filter(student=user.pk)
        dialogs = chain(
            english_dialogs.filter(is_active=True).all(),
            french_dialogs.filter(is_active=True).all()
        )

        context['exercises_dialogs'] = dialogs
        context['statistics'] = {}
        context['statistics']['lessons_done_count'] = lessons.filter(
            status='D').count()
        context['statistics']['exercises_done_count'] = get_exercises_done_count(
            english_words,
            french_words,
            irregular_verbs,
            english_dialogs,
            french_dialogs
        )
        context['statistics']['words_learned_count'] = get_words_learned_count(
            english_words,
            french_words,
            irregular_verbs,
            english_dialogs,
            french_dialogs
        )

    context['events'] = lessons
    context['courses'] = tuple(Course.objects.all())
    context['current_pane'] = current_pane

    return render(request, 'users/account/account.html', context)


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
