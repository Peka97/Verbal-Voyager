from django.urls import path

from . import views


urlpatterns = [
    path('json/load_from_api/<str:lang>',
         views.load_from_api, name='load_from_api'),
]
