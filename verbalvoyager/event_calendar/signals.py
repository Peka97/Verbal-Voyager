from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Project, Lesson, LessonTask

CACHE_KEY_PATTERN = "*.user_account_view.*"

@receiver(post_save, sender=Project)
def invalidate_my_model_cache_on_save(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)

@receiver(post_save, sender=Lesson)
def invalidate_my_model_cache_on_save(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)

@receiver(post_save, sender=LessonTask)
def invalidate_my_model_cache_on_save(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)

@receiver(post_delete, sender=Project)
def invalidate_my_model_cache_on_delete(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)

@receiver(post_delete, sender=Lesson)
def invalidate_my_model_cache_on_delete(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)

@receiver(post_delete, sender=LessonTask)
def invalidate_my_model_cache_on_delete(sender, instance, **kwargs):
    redis_client = cache._cache.get_client()
    keys = redis_client.keys(CACHE_KEY_PATTERN)
    
    if keys:
        redis_client.delete(*keys)
    
    