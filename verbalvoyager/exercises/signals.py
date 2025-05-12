import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import ExerciseCategory, ExerciseEnglishWords, ExerciseEnglishDialog, ExerciseIrregularEnglishVerb, ExerciseFrenchWords, ExerciseFrenchDialog, ExerciseRussianWords, ExerciseRussianDialog, ExerciseSpanishWords, ExerciseSpanishDialog

logger = logging.getLogger('django')


@receiver([post_save, post_delete], sender=ExerciseCategory)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_category*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseEnglishWords)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_english_words_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_english_words_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseEnglishDialog)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_english_dialogs_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_english_dialogs_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseIrregularEnglishVerb)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(
            f"global_*_exercises_exercise_english_irregular_verbs_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_english_irregular_verbs_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseFrenchWords)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_french_words_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_french_words_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseFrenchDialog)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_french_dialogs_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_french_dialogs_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseRussianWords)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_russian_words_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_russian_words_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseRussianDialog)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_russian_dialogs_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_russian_dialogs_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseSpanishWords)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_spanish_words_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_spanish_words_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=ExerciseSpanishDialog)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern(f"global_*_exercises_exercise_spanish_dialogs_*")
        cache.delete_pattern(
            f"user_*_exercises_exercise_spanish_dialogs_{instance.id}*")
    except Exception as err:
        logger.error(err, exc_info=True)
