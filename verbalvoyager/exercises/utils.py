from openai import OpenAI

from django.shortcuts import redirect, get_object_or_404
from django.http.response import Http404
from django.conf import settings
from dictionary.models import EnglishWord, FrenchWord, SpanishWord


def generate_dialog(lang: str, word_ids: list, sentence_count: int, level: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENAI_API_KEY,
    )
    
    if lang in ('english', 'russian'):
        word_obj = EnglishWord
    elif lang == 'french':
        word_obj = FrenchWord
    elif lang == 'spanish':
        word_obj = SpanishWord
    else:
        return

    word_objects = [word_obj.objects.get(pk=word_id) for word_id in word_ids]
    
    if lang == 'russian':
        words = ', '.join(word.translation for word in word_objects)
    else:
        words = ', '.join(word.word for word in word_objects)

    completion = client.chat.completions.create(
        extra_headers={
            # "HTTP-Referer": $YOUR_SITE_URL,  # Optional, for including your app on openrouter.ai rankings.
            # "X-Title": $YOUR_APP_NAME,  # Optional. Shows in rankings on openrouter.ai.
        },
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
                Ковычки и квадратные скобки из структуры выше убери в конечном варианте.
                """
            }
        ]
    )
    return completion.choices[0].message.content


def get_exercise_or_404(request, exercise_obj, ex_pk):
    exercise = get_object_or_404(exercise_obj, pk=ex_pk)

    if exercise.external_access or (request.user.is_authenticated and request.user.is_teacher()):
        pass
    else:
        if not request.user.is_authenticated:
            return None, redirect(f"/users/auth?next={request.path}")
        if exercise.student != request.user:
            raise Http404("Запрашиваемый объект не найден")

    return exercise, None
