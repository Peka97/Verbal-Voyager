from django.urls import path

from .views import json_update_lesson_plan

urlpatterns = [
    path('json/update/<int:lesson_plan_id>/', json_update_lesson_plan,
         name='json_update_lesson_plan'),
]
