import logging

from django.conf import settings
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from django.core.exceptions import ValidationError


from .models import ExerciseCategory, ExerciseWords
from dictionary.models import Translation
logger = logging.getLogger('django')

VERSION = settings.CACHES['default']['OPTIONS']['VERSION']


@receiver(m2m_changed, sender=ExerciseWords.words.through)
def validate_words_m2m(sender, instance, action, **kwargs):
    if action == "pre_add":
        for word_id in kwargs.get('pk_set', []):
            translation = Translation.objects.get(pk=word_id)

            if instance.lang and instance.lang.name == 'Russian' and translation.source_word.language.name == 'English':
                continue
            if translation.source_word.language != instance.lang:
                raise ValidationError(
                    f'Слово "{translation}" не подходит для языка "{instance.lang}"'
                )


@receiver([post_save, post_delete], sender=ExerciseCategory)
def invalidate_exercise_category_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern("global_*_exercises_category*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete, m2m_changed], sender=ExerciseWords)
def clear_exercise_words_cache(sender, instance, **kwargs):
    try:
        CACHE_KEY = f"*user_{instance.student_id}_exercises_exercise_words_{VERSION}"
        cache.delete_pattern(CACHE_KEY)
    except Exception as err:
        logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseEnglishWords)
# def invalidate_exercise_english_words_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_english_words_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_english_words_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseEnglishDialog)
# def invalidate_exercise_english_dialogs_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_english_dialogs_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_english_dialogs_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseIrregularEnglishVerb)
# def invalidate_exercise_irregular_verbs_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern(
#             "global_*_exercises_exercise_english_irregular_verbs_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_english_irregular_verbs_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseFrenchWords)
# def invalidate_exercise_french_words_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_french_words_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_french_words_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseFrenchDialog)
# def invalidate_exercise_french_dialogs_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_french_dialogs_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_french_dialogs_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseRussianWords)
# def invalidate_exercise_russian_words_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_russian_words_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_russian_words_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseRussianDialog)
# def invalidate_exercise_russian_dialogs_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_russian_dialogs_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_russian_dialogs_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseSpanishWords)
# def invalidate_exercise_spanish_words_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_spanish_words_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_spanish_words_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)


# @receiver([post_save, post_delete], sender=ExerciseSpanishDialog)
# def invalidate_exercise_spanish_dialogs_cache(sender, instance, **kwargs):
#     try:
#         cache.delete_pattern("global_*_exercises_exercise_spanish_dialogs_*")
#         cache.delete_pattern(
#             f"user_*_exercises_exercise_spanish_dialogs_{instance.id}*")
#     except Exception as err:
#         logger.error(err, exc_info=True)
