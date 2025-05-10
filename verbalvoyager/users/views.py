from ast import match_case
import logging
from collections import defaultdict
from itertools import chain

from django.db.models import Count
from django.core.cache import cache
from django.db.models import Prefetch
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required

from users.services.cache import get_cached_user_account_teacher, get_cached_lessons, get_cached_courses, get_cached_projects, get_cached_english_words, get_cached_french_words, get_cached_russian_words, get_cached_spanish_words,  get_cached_english_irregular_verbs, get_cached_english_dialogs, get_cached_french_dialogs, get_cached_russian_dialogs, get_cached_spanish_dialogs
from users.forms import RegistrationUserForm, CustomPasswordResetForm, AuthUserForm, TimezoneForm
from users.utils import get_words_learned_count, get_exercises_done_count, init_student_demo_access


logger = logging.getLogger('django')
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
            request.session.flush()
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

            request.session.flush()
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
    request.session.flush()
    logout(request)
    return redirect('')


@login_required(login_url="/users/auth")
def user_account(request):
    user = request.user
    current_pane = request.GET.get('pane')
    
    context = {
        'user_is_teacher': user.is_teacher(),
        'user_is_supervisor': user.is_supervisor(),
    }

    if request.method == 'POST':
        set_user_timezone(request)
    else:
        context['timezone_form'] = TimezoneForm(instance=request.user)

    if context['user_is_supervisor']:
        context['teachers'] = tuple(
            User.objects.filter(groups__name='Teacher').exclude(username='admin').values_list('pk', flat=True))

    if context['user_is_teacher']:
        lessons_obj = get_cached_user_account_teacher(user)
        lessons = defaultdict(list)

        for lesson in lessons_obj:
            lessons[lesson.datetime].append(lesson)

        lessons = tuple(lessons.values())
    else:
        lessons = get_cached_lessons(user)
        projects = get_cached_projects(user)
        context['projects'] = projects
        context['exercises'] = get_user_exercises(user, projects)

        # Временно отключена статистика
        # context['statistics'] = {}
        # context['statistics']['lessons_done_count'] = lessons.filter(
        #     status='D').count()
        # context['statistics']['exercises_done_count'] = get_exercises_done_count(
        #     english_words,
        #     french_words,
        #     irregular_verbs,
        #     english_dialogs,
        #     french_dialogs
        # )
        # context['statistics']['words_learned_count'] = get_words_learned_count(
        #     english_words,
        #     french_words,
        #     irregular_verbs,
        #     english_dialogs,
        #     french_dialogs
        # )

    context['events'] = lessons
    context['courses'] = get_cached_courses(request.user)
    context['current_pane'] = current_pane

    return render(request, 'users/account/account.html', context)

def set_user_timezone(request):
    form = TimezoneForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Часовой пояс успешно обновлен.')
        url = reverse('account', kwargs={'current_pane': 'profile'})
        return redirect(url)
    else:
        messages.error(request, 'Ошибка при обновлении часового пояса.')

def get_user_exercises(user, projects):
    result = []
    unique_courses = {p.course_id.name for p in projects}
    
    for course in unique_courses:
        match course:
            case "Английский язык":
                result.append(
                    get_cached_english_words(user)
                )
                result.append(
                    get_cached_english_dialogs(user)
                )
                result.append(
                    get_cached_english_irregular_verbs(user)
                )
            case "Французский язык":
                result.append(
                    get_cached_french_words(user)
                )
                result.append(
                    get_cached_french_dialogs(user)
                )
            case "Русский язык":
                result.append(
                    get_cached_russian_words(user)
                )
                result.append(
                    get_cached_russian_dialogs(user)
                )
            case "Испанский язык":
                result.append(
                    get_cached_spanish_words(user)
                )
                result.append(
                    get_cached_spanish_dialogs(user)
                )
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
