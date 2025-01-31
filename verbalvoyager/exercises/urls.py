from django.urls import path, include
from django.contrib.auth import views, get_user_model
from . import views
from pages.views import handler_403, handler_404, handler_500


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('words/english/<int:ex_id>/<int:step>',
         views.exercises_words_english, name='exercises_words_english'),
    path('words/french/<int:ex_id>/<int:step>',
         views.exercises_words_french, name='exercises_words_french'),
#     path('words/update/<int:ex_id>/<str:step_num>',
#          views.exercises_words_update, name='exercises_words_update'),
    path('dialog/<int:ex_id>', views.exercises_dialog, name='exercises_dialog'),
    path('dialog/english/<int:ex_id>', views.exercises_dialog_english, name='exercises_dialog_english'),
    path('dialog/french/<int:ex_id>', views.exercises_dialog_french, name='exercises_dialog_french'),
    path('dialog/english/update/<int:ex_id>', views.exercises_dialog_english_update,
         name='exercises_dialog_english_update'),
    path('dialog/french/update/<int:ex_id>', views.exercises_dialog_french_update,
         name='exercises_dialog_french_update'),
    path('logging/<int:ex_id>/<str:step_num>', views.logging, name='logging'),

    path('dialog/json/generate_dialog/english', views.generate_dialog_english_json, name='generate_dialog_english_json'),
    path('dialog/json/generate_dialog/french', views.generate_dialog_french_json, name='generate_dialog_french_json'),

]
