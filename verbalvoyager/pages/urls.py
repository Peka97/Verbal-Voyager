from django.urls import path
from django.contrib import admin

from . import views
from pages.views import handler_403, handler_404, handler_500


urlpatterns = [
    path('', views.index, name=''),
    path('english', views.english_course, name='english'),
    path('french', views.french_course, name='french'),
    path('spanish', views.spanish_course, name='spanish'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('about', views.about_project, name='about'),
    path('contacts', views.contacts, name='contacts'),
    path('faq', views.faq, name='faq'),

    path('403', handler_403, name='err_403'),
    path('404', handler_404, name='err_404'),
    path('500', handler_500, name='err_500'),
]
