from django.urls import path, include
from django.contrib.auth import views, get_user_model
from . import views
from pages.views import handler_403, handler_404, handler_500


handler403 = handler_403
handler404 = handler_404
handler500 = handler_500

urlpatterns = [
    path('<int:ex_id>/<int:step>', views.exercises_words, name='exercises_words'),
    path('update/<int:ex_id>/<str:step_num>', views.update, name='ex_update')
]
