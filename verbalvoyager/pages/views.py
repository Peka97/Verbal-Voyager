import logging

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import TemplateView

from event_calendar.models import Review
from users.services.cache import get_cached_courses


logger = logging.getLogger('django')
User = get_user_model()


class AbstractHandler(TemplateView):
    template_name = 'pages/error.html'


class Handler403(AbstractHandler):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ошибка доступа: 403'
        context['error_message'] = 'Доступ к странице ограничен.'
        return context


class Handler404(AbstractHandler):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страница не найдена: 404'
        context['error_message'] = 'К сожалению такая страница была не найдена.'
        return context


class Handler500(AbstractHandler):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ошибка сервера: 500'
        context['error_message'] = 'Внутренняя ошибка сайта, вернитесь на главную страницу.'
        return context


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = get_cached_courses()
        reviews = Review.objects.order_by('?')[:3].values(
            'course__name', 'text', 'created_at', 'from_user__first_name')

        for review in reviews:
            review['created_at'] = review['created_at'].strftime("%d.%m.%Y")

        context['reviews'] = reviews
        # context['student_count'] = {
        #     'english': Project.objects.filter(course_id__name='Английский язык').count(),
        #     'french': Project.objects.filter(course_id__name='Французский язык').count(),
        #     'spanish': Project.objects.filter(course_id__name='Испанский язык').count(),
        #     'russian': Project.objects.filter(course_id__name='Русский язык').count(),
        #     'сhinese': Project.objects.filter(course_id__name='Китайский язык').count(),
        # }
        return context


class EnglishCourseView(TemplateView):
    template_name = 'pages/english_course.html'


class FrenchCourseView(TemplateView):
    template_name = 'pages/french_course.html'


class SpanishCourseView(TemplateView):
    template_name = 'pages/spanish_course.html'


class RussianCourseView(TemplateView):
    template_name = 'pages/russian_course.html'


class ChineseCourseView(TemplateView):
    template_name = 'pages/chinese_course.html'


class PortfolioView(TemplateView):
    template_name = 'pages/portfolio.html'


class AboutProjectView(TemplateView):
    template_name = 'pages/about.html'


class ContactsView(TemplateView):
    template_name = 'pages/contacts.html'


class FaqView(TemplateView):
    template_name = 'pages/faq.html'
