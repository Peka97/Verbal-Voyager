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
        lessons = list(Lesson.objects.filter(teacher_id=user.pk).order_by(
            'datetime').all().prefetch_related('students'))

        context['events'] = lessons
        context['events_count_total'] = len(lessons)
    else:
        lessons = list(Lesson.objects.filter(
            students=user).order_by('datetime').select_related('teacher_id').all()
        )

        context['projects'] = Project.objects.filter(students=user).all()
        context['exercises'] = list(ExerciseWords.objects.filter(
            student=user.pk,
            is_active=True
        ).all())
        context['dialogs'] = list(ExerciseDialog.objects.filter(
            student=user.pk,
            is_active=True
        ).all())
        context['events'] = lessons
        context['events_count_total'] = len(lessons)
        context['events_count_done'] = len(
            [lesson for lesson in lessons if lesson.status == 'D']
        )

    context['courses'] = list(Course.objects.all())
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
