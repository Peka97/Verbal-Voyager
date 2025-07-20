from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name=''),
    # path('english', views.english_course, name='english'),
    path('english', views.ContactsView.as_view(), name='english'),
    # path('french', views.french_course, name='french'),
    path('french', views.ContactsView.as_view(), name='french'),
    # path('spanish', views.spanish_course, name='spanish'),
    path('spanish', views.ContactsView.as_view(), name='spanish'),
    path('portfolio', views.PortfolioView.as_view(), name='portfolio'),
    path('about', views.AboutProjectView.as_view(), name='about'),
    path('contacts', views.ContactsView.as_view(), name='contacts'),
    path('faq', views.FaqView.as_view(), name='faq'),
]
