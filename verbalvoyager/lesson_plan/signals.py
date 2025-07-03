import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import EnglishLessonPlan


logger = logging.getLogger('django')


@receiver([post_save, post_delete], sender=EnglishLessonPlan)
def invalidate_english_lesson_plan_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(
            f"user_{instance.lesson_id.teacher_id.id}_lessons*")
        cache.delete_pattern(
            f"user_{instance.lesson_id.student_id.id}_lessons*")
    except Exception as err:
        logger.error(err, exc_info=True)
