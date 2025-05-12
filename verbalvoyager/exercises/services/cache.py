from django.core.cache import cache


def get_cached_global_exercise(exercise_obj, exercise_id):
    CACHE_KEY = f"user_exercises_{exercise_obj.__class__.__name__.lower()}_{exercise_id}"
    return cache.get_or_set(
        CACHE_KEY,
        lambda: exercise_obj.objects.get(pk=exercise_id),
        timeout=3600
    )
