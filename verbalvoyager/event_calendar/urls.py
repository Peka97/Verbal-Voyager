from django.urls import path

from . import views

urlpatterns = [
    path('json/filter_lessons_by_student/<int:student_id>',
         views.filter_lessons_by_student, name='filter_lessons_by_student'),
    path('json/update/', views.update, name='update'),
    path('json/load_student_lessons/<int:student_id>/',
         views.load_student_lessons, name='load_student_lessons'),
    path('json/load_teacher_lessons/<int:teacher_id>/',
         views.load_teacher_lessons, name='load_teacher_lessons'),
]
