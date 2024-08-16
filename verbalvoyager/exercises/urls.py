from django.urls import path, include
from django.contrib.auth import views, get_user_model
from . import views
from pages.views import handler_403, handler_404, handler_500


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('words/<int:ex_id>/<int:step>', views.exercises_words, name='exercises_words'),
    path('words/update/<int:ex_id>/<str:step_num>', views.exercises_words_update, name='exercises_words_update'),
    path('dialog/<int:ex_id>', views.exercises_dialog, name='exercises_dialog'),
    path('dialog/update/<int:ex_id>', views.exercises_dialog_update, name='exercises_dialog_update'),

]
