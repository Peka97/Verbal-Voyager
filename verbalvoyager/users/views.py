from collections import defaultdict
from itertools import chain

from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView
from django.contrib import messages

from logger import get_logger
from users.forms import RegistrationUserForm, CustomPasswordResetForm, AuthUserForm, TimezoneForm
from users.utils import get_words_learned_count, get_exercises_done_count, init_student_demo_access
from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseRussianWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb
from event_calendar.models import Lesson, Project, Course


logger = get_logger()
User = get_user_model()


def user_auth(request):
    context = {
        'auth_show': True
    }

    next = request.GET.get('next')

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(next) if next else redirect('')
        else:
            context['auth_error'] = 'Неправильное имя пользователя или пароль'
    else:
        context['auth_form'] = AuthUserForm()
        context['sign_in_form'] = RegistrationUserForm()

    return render(request, 'users/auth.html', context)

def user_register(request):
    context = {
        'auth_show': False
    }
    
    if request.POST:
        form = RegistrationUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            login(request, user)
            
            try:
                init_student_demo_access(user)
            except Exception:
                logger.error(f'Fail create demo exercises: {user}', exc_info=True)
                
            return redirect('')
        else:
            context['sign_in_form'] = form
            context['auth_show'] = False
    else:
        context['auth_form'] = AuthUserForm()
        context['sign_in_form'] = RegistrationUserForm()
        
    return render(request, 'users/auth.html', context)


def user_logout(request):
    logout(request)
    return redirect('')


@login_required(login_url="/users/auth")
def user_account(request, current_pane):
    user = request.user

    context = {
        'user_is_teacher': user.is_teacher()
    }

    if request.method == 'POST':
        form = TimezoneForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Часовой пояс успешно обновлен.')
            url = reverse('account', kwargs={'current_pane': 'profile'})
            return redirect(url)
        else:
            messages.error(request, 'Ошибка при обновлении часового пояса.')
    else:
        context['timezone_form'] = TimezoneForm(instance=request.user)

    if user.is_supervisor():
        context['teachers'] = tuple(
            User.objects.filter(groups__name='Teacher').exclude(username='admin').values_list('pk', flat=True))

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
        english_words, french_words, russian_words = ExerciseEnglishWords.objects.filter(student=user.pk), \
            ExerciseFrenchWords.objects.filter(student=user.pk), \
            ExerciseRussianWords.objects.filter(student=user.pk)
        context['exercises_words'] = tuple(chain(
            english_words.all(),
            french_words.all(),
            russian_words.all()
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
