from openai import OpenAI
from pprint import pprint

from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import Http404

from verbalvoyager.settings import OPENAI_API_KEY
from dictionary.models import EnglishWord, FrenchWord


def generate_dialog(lang: str, word_ids: list, sentence_count: int, level: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )
    # pprint(client.models.list())  # Output all models
    if lang == 'английском':
        word_obj = EnglishWord
    if lang == 'французском':
        word_obj = FrenchWord

    word_objects = [word_obj.objects.get(pk=word_id) for word_id in word_ids]
    words = ', '.join(word.word for word in word_objects)
    print(words)

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
                Используй сделующую структуру:\n 
                *здесь краткое описание ситуации, в которой находятся друзья*
                *имя первого друга*: *текст*
                *имя второго друга*: *текст*
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
            return redirect(f"/users/auth?next={request.path}")
        if exercise.student != request.user:
            raise Http404("Запрашиваемый объект не найден")

    return exercise
