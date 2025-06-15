from django.urls import path

from . import views


urlpatterns = [
    path('json/load_from_api/',
         views.load_from_api, name='load_from_api'),
    path('json/get_translation/<str:lang>/',
         views.get_translation, name='get_translation')
]
