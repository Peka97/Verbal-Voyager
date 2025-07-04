import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    FormView,
    PasswordResetCompleteView,
    PasswordResetView,
)
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView, UpdateView

from users.forms import (
    AuthUserForm,
    CustomPasswordResetForm,
    RegistrationUserForm,
    TimezoneForm,
)
from users.services.cache import (
    get_cached_all_teachers,
    get_cached_courses,
    get_cached_projects,
)
from users.services.utils import get_user_exercises
from users.utils import (
    get_exercises_done_count,
    get_lessons_done_count,
    get_words_learned_count,
    init_student_demo_access,
)


logger = logging.getLogger('django')
User = get_user_model()


class UserAuthRegisterView(FormView):
    template_name = 'users/auth.html'
    success_url = reverse_lazy('account')

    def get_form_class(self):
        return RegistrationUserForm if self.request.POST.get('action') == 'register' else AuthUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'auth_form': AuthUserForm(),
            'sign_in_form': RegistrationUserForm(),
            'auth_show': self.request.POST.get('action') != 'register'
        })

        return context

    def form_valid(self, form):
        action = self.request.POST.get('action')

        if action == 'register':
            user = form.save(commit=False)
            user.save()

            self.request.session.flush()
            login(self.request, user)

            try:
                init_student_demo_access(user)
            except Exception:
                logger.error(
                    f'Fail create demo exercises: {user}', exc_info=True)

        elif action == 'login':
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(
                self.request, username=username, password=password)

            if not user:
                form.add_error(
                    None, 'Неправильное имя пользователя или пароль')
                return self.form_invalid(form)

            self.request.session.flush()
            login(self.request, user)
        else:

            return Http404()

        next_url = self.request.GET.get('next', self.success_url)

        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            next_url = self.success_url

        return redirect(next_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)


class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_pane = self.request.GET.get('pane', 'activities')

        context.update({
            'user_is_teacher': user.is_teacher(),
            'user_is_supervisor': user.is_supervisor(),
            'timezone_form': TimezoneForm(instance=user),
            'courses': get_cached_courses(),
            'current_pane': current_pane,
        })

        if context['user_is_supervisor']:
            context['teachers'] = tuple(get_cached_all_teachers())

        if not context['user_is_teacher']:
            projects = get_cached_projects(user)
            exercises = get_user_exercises(user, projects)
            context.update({
                'projects': projects,
                'exercises': exercises,
                'statistics': {
                    'lessons_done_count': get_lessons_done_count(user),
                    'exercises_done_count': get_exercises_done_count(exercises),
                    'words_learned_count': get_words_learned_count(exercises),
                }
            })

        return context

    def post(self, request, *args, **kwargs):
        form = TimezoneForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Часовой пояс успешно обновлен.')
        else:
            messages.error(request, 'Ошибка при обновлении часового пояса.')

        return self.get(request, *args, **kwargs)


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


class SetUserTimezoneView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = TimezoneForm
    success_url = reverse_lazy('account')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Часовой пояс успешно обновлен.')
        return JsonResponse({'status': 'success', 'message': 'Часовой пояс успешно обновлен.'})

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при обновлении часового пояса.')
        return JsonResponse({'status': 'error', 'message': 'Ошибка при обновлении часового пояса.', 'errors': form.errors})
