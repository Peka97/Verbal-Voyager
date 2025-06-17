import logging
from collections import defaultdict

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme


from users.services.cache import get_cached_all_teachers, get_cached_lessons_for_teacher, get_cached_lessons_for_student, get_cached_courses, get_cached_projects, get_cached_user_english_words, get_cached_user_french_words, get_cached_user_russian_words, get_cached_user_spanish_words,  get_cached_user_english_irregular_verbs, get_cached_user_english_dialogs, get_cached_user_french_dialogs, get_cached_user_russian_dialogs, get_cached_user_spanish_dialogs
from users.services.cache import get_cached_user_words, get_cached_user_dialogs, get_cached_user_english_irregular_verbs
from users.forms import RegistrationUserForm, CustomPasswordResetForm, AuthUserForm, TimezoneForm
from users.utils import get_words_learned_count, get_exercises_done_count, init_student_demo_access


logger = logging.getLogger('django')
User = get_user_model()


def user_auth(request):
    context = {
        'auth_show': True,
        'auth_form': AuthUserForm(),
        'sign_in_form': RegistrationUserForm()
    }

    next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = settings.LOGIN_REDIRECT_URL

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            context['auth_error'] = 'Неправильное имя пользователя или пароль'
        else:
            request.session.flush()
            login(request, user)
            return redirect(next_url)

    return render(request, 'users/auth.html', context)


def user_register(request):
    context = {
        'auth_show': False,
        'auth_form': AuthUserForm(),
        'sign_in_form': RegistrationUserForm()
    }

    if request.POST:
        form = RegistrationUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            request.session.flush()
            login(request, user)

            try:
                init_student_demo_access(user)
            except Exception:
                logger.error(
                    f'Fail create demo exercises: {user}', exc_info=True)

            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context['sign_in_form'] = form

    return render(request, 'users/auth.html', context)


def user_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def user_account(request):
    user = request.user
    current_pane = request.GET.get('pane')

    if not current_pane:
        current_pane = 'activities'

    context = {
        'user_is_teacher': user.is_teacher(),
        'user_is_supervisor': user.is_supervisor(),
    }

    if request.method == 'POST':
        context['timezone_form'] = set_user_timezone(request)
    else:
        context['timezone_form'] = TimezoneForm(instance=request.user)

    if context['user_is_supervisor']:
        context['teachers'] = tuple(get_cached_all_teachers())

    if context['user_is_teacher']:
        lessons_obj = get_cached_lessons_for_teacher(user)
        lessons = defaultdict(list)

        for lesson in lessons_obj:

            if hasattr(lesson, 'lesson_plan'):
                print(lesson)
                print(lesson.lesson_plan)
                print(lesson.lesson_plan.new_vocabulary.all())
            lessons[lesson.datetime].append(lesson)

        lessons = tuple(lessons.values())
    else:
        lessons = get_cached_lessons_for_student(user)
        projects = get_cached_projects(user)
        exercises = get_user_exercises(user, projects)
        context['projects'] = projects
        context['exercises'] = exercises

        # Временно отключена статистика
        context['statistics'] = {}
        context['statistics']['lessons_done_count'] = lessons.filter(
            status='D').count()
        context['statistics']['exercises_done_count'] = get_exercises_done_count(
            exercises
        )
        context['statistics']['words_learned_count'] = get_words_learned_count(
            exercises
        )

    context['events'] = lessons
    context['courses'] = get_cached_courses()
    context['current_pane'] = current_pane

    return render(request, 'users/account/account.html', context)


def set_user_timezone(request):
    form = TimezoneForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Часовой пояс успешно обновлен.')
    else:
        messages.error(request, 'Ошибка при обновлении часового пояса.')
    return form


def get_user_exercises(user, projects):
    result = [
        *get_cached_user_words(user),
        *get_cached_user_dialogs(user),
        *get_cached_user_english_irregular_verbs(user),
    ]
    # TODO: add sort for created_at field
    result.sort(key=lambda exer: exer.is_active, reverse=True)
    return result

# TODO: обновление таймзоны без обновления страницы
# def json_update_timezone(request):
#     if request.method == 'POST':
#         try:
#             timezone = json.loads(request.body)['timezone']
#         except (KeyError, json.decoder.JSONDecodeError):
#             return JsonResponse({'error': 'Invalid data'}, status=400)

#         print(timezone)

#         user = User.objects.get(request.user.id)
#         print(user)
#         # user.timezone = timezone
#         # user.save()

#         return JsonResponse({'result': 'Timezone updated'}, status=200)


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
