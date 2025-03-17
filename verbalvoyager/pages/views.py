
from django.shortcuts import render
from django.contrib.auth import get_user_model

from event_calendar.models import Review, Course
from logger import get_logger


logger = get_logger()
User = get_user_model()


def handler_403(request, exception=None):
    context = {
        'title': 'Ошибка доступа: 403',
        'error_message': 'Доступ к этой странице ограничен.',
    }
    return render(request, 'pages/error.html', context, status=403)


def handler_404(request, exception=None):
    context = {
        'title': 'Страница не найдена: 404',
        'error_message': 'К сожалению такая страница была не найдена.',
    }
    return render(request, 'pages/error.html', context, status=404)


def handler_500(request, exception=None):
    context = {
        'title': 'Ошибка сервера: 500',
        'error_message': 'Внутренняя ошибка сайта, вернитесь на главную страницу.',
    }
    return render(request, 'pages/error.html', context, status=500)


def index(request):
    context = {}

    user = request.user
    courses = list(Course.objects.all())
    reviews = list(Review.objects.order_by('?').values(
        'course__name', 'text', 'created_at', 'from_user__first_name')[:3])

    for review in reviews:
        review['created_at'] = review['created_at'].strftime("%d.%m.%Y")

    context['user'] = user
    context['courses'] = courses
    context['reviews'] = reviews

    return render(request, 'pages/index.html', context)


def english_course(request):
    context = {}
    return render(request, 'pages/english_course.html', context)


def french_course(request):
    context = {}
    return render(request, 'pages/french_course.html', context)


def spanish_course(request):
    context = {}
    return render(request, 'pages/spanish_course.html', context)


def portfolio(request):
    context = {}
    return render(request, 'pages/portfolio.html', context)


def about_project(request):
    context = {}
    return render(request, 'pages/about.html', context)


def contacts(request):
    context = {}
    return render(request, 'pages/contacts.html', context)


def faq(request):
    context = {}
    return render(request, 'pages/faq.html', context)
