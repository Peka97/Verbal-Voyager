from .models import EnglishWord, FrenchVerb, SpanishWord


def get_word_class_name(ex_lang: str) -> EnglishWord | FrenchVerb | SpanishWord | None:
    word_obj_name = f"{ex_lang.capitalize()}Word"
    return globals().get(word_obj_name)
