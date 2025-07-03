import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Lesson, LessonTask, Project


logger = logging.getLogger('django')


@receiver([post_save, post_delete], sender=Lesson)
def invalidate_lesson_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"user_{instance.teacher_id.id}_lessons*")
        cache.delete_pattern(f"user_{instance.student_id.id}_lessons*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=LessonTask)
def invalidate_lesson_task_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(
            f"user_{instance.lesson_id.teacher_id.id}_lesson_tasks*")
        cache.delete_pattern(
            f"user_{instance.lesson_id.student_id.id}_lesson_tasks*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=Project)
def invalidate_project_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"user_{instance.teacher_id.id}_projects*")
        for student in instance.students.all():
            cache.delete_pattern(f"user_{student.id}_projects*")
    except Exception as err:
        logger.error(err, exc_info=True)
