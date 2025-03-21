import logging
import json

from pprint import pprint

from django.http import JsonResponse
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.db import transaction
from .models import Lesson, LessonTask, ProjectTask

from verbalvoyager.settings import DEBUG_LOGGING_FP

log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(DEBUG_LOGGING_FP)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)


def filter_lessons_by_student(request, student_id):
    products = Lesson.objects.filter(students=student_id)
    return JsonResponse({x.id: str(x) for x in products})

def update(request):
    data = json.loads(request.body)
    
    if data.get('tasks'):
        tasks_obj = LessonTask.objects.filter(pk__in=data['tasks'].keys()).all()
        tasks = {task.pk: task for task in tasks_obj}
        
        for task_pk, task_status in data['tasks'].items():
            updated_task = tasks.get(int(task_pk))
            if updated_task:
                updated_task.is_completed = task_status
        
        with transaction.atomic():
            LessonTask.objects.bulk_update(tasks.values(), ('is_completed',))
    
    if data.get('lessons'):
        lesson_obj = Lesson.objects.filter(pk__in=data['lessons'].keys()).all()
        lessons = {lesson.pk: lesson for lesson in lesson_obj}
        
        for lesson_pk, lesson_status in data['lessons'].items():
            updated_lesson = lessons.get(int(lesson_pk))
            
            if updated_lesson:
                
                if lesson_status.get('performing') is not None:
                    updated_lesson.status = lesson_status['performing']
                if lesson_status.get('payment') is not None:
                    updated_lesson.is_paid = lesson_status['payment']
        
        with transaction.atomic():
            Lesson.objects.bulk_update(lessons.values(), ('status', 'is_paid',))
            
        
    return JsonResponse({'status': 'OK'})