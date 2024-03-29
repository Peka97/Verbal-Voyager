from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name=''),
    path('admin/', admin.site.admin_view, name='admin'),
    path('english', views.english_course, name='english'),
    path('french', views.french_course, name='french'),
    path('spanish', views.spanish_course, name='spanish'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('about', views.about_project, name='about'),
    path('contacts', views.contacts, name='contacts'),
    path('faq', views.faq, name='faq'),
    path('test', views.test, name='test'),
]
