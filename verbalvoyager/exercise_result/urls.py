from django.urls import path

from . import views


urlpatterns = [
    path('<str:ex_type>/<int:ex_id>/<str:step_num>',
         views.exercise_result_update, name='exercise_result_update'),
]
