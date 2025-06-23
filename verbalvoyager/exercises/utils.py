from openai import OpenAI

from django.shortcuts import redirect
from django.http.response import Http404
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from dictionary.models import Translation
from .services.cache import get_cached_global_exercise
from dictionary.models import Translation, Word


# def generate_dialog(lang: str, word_ids: list, sentence_count: int, level: str) -> str:
#     client = OpenAI(
#         base_url="https://openrouter.ai/api/v1",
#         api_key=settings.OPENAI_API_KEY,
#     )

#     word_objects = [Word.objects.get(pk=word_id) for word_id in word_ids]

#     if lang == 'russian':
#         words = ', '.join(word.translation for word in word_objects)
#     else:
#         words = ', '.join(word.word for word in word_objects)

#     completion = client.chat.completions.create(
#         extra_headers={
#             # "HTTP-Referer": $YOUR_SITE_URL,  # Optional, for including your app on openrouter.ai rankings.
#             # "X-Title": $YOUR_APP_NAME,  # Optional. Shows in rankings on openrouter.ai.
#         },
#         model="deepseek/deepseek-chat",
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"""
#                 Придумай небольшой диалог ({sentence_count} реплик на каждого) двух друзей на {lang} языке с использованием следующих слов: {words}.
#                 Уровень языка {level}.
#                 Используй строго следующую структуру:\n
#                 "Situation: [здесь краткое описание ситуации, в которой находятся друзья]\n
#                 [имя первого друга]: [текст]\n
#                 [имя второго друга]: [текст]"\n
#                 Ковычки и квадратные скобки из структуры выше убери в конечном варианте.
#                 """
#             }
#         ]
#     )
#     return completion.choices[0].message.content


def new_generate_dialog(lang: str, word_ids: list, sentence_count: int, level: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENAI_API_KEY,
    )

    translation_objects = Translation.objects.filter(pk__in=word_ids)

    if lang == 'Russian':
        words = ', '.join(
            translation.target_word.word for translation in translation_objects)
    else:
        words = ', '.join(
            translation.source_word.word for translation in translation_objects)

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": f"""
                Придумай небольшой диалог ({sentence_count} реплик на каждого) двух друзей на {lang} языке с использованием следующих слов: {words}. 
                Уровень языка {level}.
                Используй строго следующую структуру:\n 
                "Situation: [здесь краткое описание ситуации, в которой находятся друзья]\n
                [имя первого друга]: [текст]\n
                [имя второго друга]: [текст]"\n
                Кавычки и квадратные скобки из структуры выше убери в конечном варианте.
                """
            }
        ]
    )
    return completion.choices[0].message.content


def get_exercise_or_404(request, exercise_obj, exercise_id):
    exercise = get_cached_global_exercise(exercise_obj, exercise_id)

    if not exercise.external_access and isinstance(request.user, AnonymousUser):
        return None, redirect(f"/users/auth?next={request.path}")

    if exercise.student != request.user and not request.user.is_teacher():
        raise Http404("Запрашиваемый объект не найден")

    return exercise, None


def check_exercise_access(request, exercise_obj):
    if not exercise_obj.external_access and isinstance(request.user, AnonymousUser):
        return False, redirect(f"/users/auth?next={request.path}")

    if exercise_obj.student != request.user and not request.user.is_teacher():
        raise Http404("Запрашиваемый объект не найден")

    return True, None
