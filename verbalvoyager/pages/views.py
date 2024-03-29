import logging
from random import shuffle
import datetime as dt

from django.shortcuts import render, HttpResponse
from django.contrib.auth import get_user_model

from pages.models import Review

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(
    '/home/peka97/Django-Lang-Site/lang_school/logs/debug.log')
)

User = get_user_model()


def index(request):
    reviews = list(Review.objects.all())
    shuffle(reviews)
    reviews = reviews[:3]

    for review in reviews:
        review.date = f'{review.datetime.day}.{review.datetime.month}.{review.datetime.year}'

    context = {
        'reviews': reviews,
        'user': User.objects.get(username=request.user)
    }
    return render(request, 'pages/index.html', context)
    # return HttpResponse('Index Page OK')


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


def test(request):
    context = {}
    return render(request, 'pages/test.html', context)
