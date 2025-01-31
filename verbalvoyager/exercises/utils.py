from openai import OpenAI
from pprint import pprint

from verbalvoyager.settings import OPENAI_API_KEY


def generate_dialog(lang: str, words: list, sentence_count: int, level: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )
    # pprint(client.models.list())  # Output all models

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