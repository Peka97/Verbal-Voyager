from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Project, Lesson, LessonTask


@receiver(post_save, sender=Lesson)
@receiver(post_delete, sender=Lesson)
def invalidate_project_cache(sender, instance, **kwargs):
    cache.delete_pattern(f"user_{instance.teacher_id.id}_lessons*")
    cache.delete_pattern(f"user_{instance.student_id.id}_lessons*")


@receiver(post_save, sender=LessonTask)
@receiver(post_delete, sender=LessonTask)
def invalidate_project_cache(sender, instance, **kwargs):
    cache.delete_pattern(f"user_{instance.lesson_id.teacher_id.id}_lesson_tasks*")
    cache.delete_pattern(f"user_{instance.lesson_id.student_id.id}_lesson_tasks*")

@receiver(post_save, sender=Project)
@receiver(post_delete, sender=Project)
def invalidate_project_cache(sender, instance, **kwargs):
    cache.delete_pattern(f"user_{instance.teacher_id.id}_projects*")
    for student in instance.students.all():
        cache.delete_pattern(f"user_{student.id}_projects*")