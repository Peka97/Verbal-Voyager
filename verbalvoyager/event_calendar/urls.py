from django.urls import path
from . import views

urlpatterns = [
    path('json/filter_lessons_by_student/<int:student_id>', views.filter_lessons_by_student, name='filter_lessons_by_student'),
]
