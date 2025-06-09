from django.urls import path

from . import views
from pages.views import handler_403, handler_404, handler_500


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    # [New] ExerciseWords
    path('v2/<str:ex_type>/<str:ex_lang>/<int:ex_id>/<int:step>',
         views.new_exercise_words, name='new_exercise_words'),

    # Words
    path('words/<str:ex_lang>/<int:ex_id>/<int:step>',
         views.exercise_words, name='exercise_words'),

    # Dialogs
    path('dialog/<str:ex_lang>/<int:ex_id>',
         views.exercise_dialog, name='exercise_dialog'),

    # Irregular Verbs
    path('irregular_verbs/<int:ex_id>/<int:step>',
         views.exercise_irregular_verbs, name='exercise_irregular_verbs'),
    path('irregular_verbs/v2/<int:ex_id>/<int:step>',
         views.new_exercise_irregular_verbs, name='new_exercise_irregular_verbs'),

    # Dialogs Generate
    path('dialog/json/generate_dialog',
         views.generate_dialog_json, name='generate_dialog_json'),
    path('dialog/json/generate_dialog/english',
         views.generate_dialog_english_json, name='generate_dialog_english_json'),
    path('dialog/json/generate_dialog/french',
         views.generate_dialog_french_json, name='generate_dialog_french_json'),

    # Exercise Logging
    path('logging/<int:ex_id>/<str:step_num>', views.words_logging),
]
