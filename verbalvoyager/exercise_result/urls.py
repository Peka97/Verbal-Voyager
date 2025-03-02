from django.urls import path

from . import views

urlpatterns = [
    # Words Updating
    path('<str:ex_type>/<str:ex_lang>/<int:ex_id>/<str:step_num>',
         views.exercise_result_update, name='exercise_result_update'),

    # Dialogs Updating
    path('<str:ex_type>/<str:ex_lang>/<int:ex_id>',
         views.exercise_result_update, name='exercise_result_update'),
]
