from django.urls import path, include
from django.contrib.auth import views, get_user_model
from . import views


urlpatterns = [
    path('<int:id>/<int:step>', views.exercises_words, name='exercises_words'),
    path('update/<int:id>', views.update, name='ex_update')
]
