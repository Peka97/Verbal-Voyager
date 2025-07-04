

def normalize_russian_word(words_qs):
    for word in words_qs:
        # word = words_qs.first()
        normalize_word = word.word.replace('*', '').rstrip(' ')
        print(f"Normalize word: {normalize_word}. Old: {word}")

        normalize_word_qs = Word.objects.filter(
            word=normalize_word, language=russian_lang)

        if normalize_word_qs.exists():
            print('Word exists')
            normalize_word_obj = normalize_word_qs.first()
        else:
            print('Create new word')

            normalize_word_obj = Word(
                word=normalize_word, language=russian_lang)
            normalize_word_obj.save()

        translation_qs = Translation.objects.filter(target_word=word)
        translation_qs_count = translation_qs.count()
        print(f'Translations: {translation_qs_count}')

        if translation_qs_count == 0:
            print('Delete old word')
            word.delete()
            continue

        for trans in translation_qs.all():
            print(
                f"Old word ID: {trans.target_word.id}. New word ID: {normalize_word_obj.id}")
            trans.target_word = normalize_word_obj
            trans.save()

        # break


def delete_translation_duplicates(translation_qs, words_lang):
    translation_qs = Translation.objects.filter(
        source_word__language=words_lang).all()

    for trans in translation_qs:
        check_duplicate = Translation.objects.filter(
            source_word=trans.source_word,
            target_word=trans.target_word,
            part_of_speech=trans.part_of_speech,
            definition=trans.definition,
            prefix=trans.prefix
        ).count()

        check_2 = Translation.objects.filter(
            source_word=trans.source_word,
            target_word=trans.target_word,
        )
        word_with_empty_str_qs = check_2.filter(
            part_of_speech='', definition='', prefix='')
        word_with_none_qs = check_2.filter(
            part_of_speech='', definition='', prefix='')

        check_hidden_duplicate = all(
            (
                word_with_empty_str_qs.exists(),
                word_with_none_qs.exists()
            )
        )

        if check_duplicate > 1:
            print(f"[{trans.source_word}] Count: {check_duplicate}")
            trans.delete()
            print(f"{trans} delete")

        if check_hidden_duplicate:
            print(f"[{trans.source_word}] Count: {check_hidden_duplicate} hidden")
            word_with_empty_str_qs.first().delete()
            print(f"{word_with_empty_str_qs} delete")


def create_translation(words_qs, source_lang, target_lang):
    words = words_qs.all()

    for word in words:
        sc_word_obj = None
        tg_word_obj = None
        source_word = word.word
        target_word = word.translation

        if source_word and len(source_word) < 50:

            sc_word_obj = Word.objects.filter(
                word=source_word, language=source_lang
            )
            print(source_word, target_word)

            if not sc_word_obj.exists():
                sc_word_obj = Word.objects.create(
                    word=source_word, language=source_lang)
                sc_word_obj.save()
            else:
                sc_word_obj = sc_word_obj.first()

            if isinstance(word, FrenchWord) and not hasattr(word, 'genus'):
                FrenchWordDetail(word=sc_word_obj, genus=word.genus).save()

        if target_word and len(target_word) < 50:

            tg_word_obj = Word.objects.filter(
                word=target_word, language=target_lang
            )
            if not tg_word_obj.exists():
                tg_word_obj = Word.objects.create(
                    word=target_word, language=target_lang)
                tg_word_obj.save()
            else:
                tg_word_obj = tg_word_obj.first()

        if sc_word_obj and tg_word_obj:
            trans_obj = Translation.objects.create(
                source_word=sc_word_obj, target_word=tg_word_obj)
            trans_obj.save()


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verbalvoyager.settings')
    django.setup()

    from dictionary.models import FrenchWord
    from dictionary.models import Language, Word, Translation
    from dictionary.models import FrenchWordDetail

    english_lang = Language.objects.get(name='English')
    french_lang = Language.objects.get(name='French')
    spanish_lang = Language.objects.get(name='Spanish')
    russian_lang = Language.objects.get(name='Russian')

    # english_words_qs = Word.objects.filter(language=english_lang)
    # delete_translation_duplicates(english_words_qs, english_lang)

    # french_words_qs = FrenchWord.objects
    # delete_translation_duplicates(french_words_qs, french_lang)

    # spanish_words_qs = SpanishWord.objects
    # delete_translation_duplicates(spanish_words_qs, spanish_lang)

    # Start English translate
    # from skyeng import load_from_api

    # translation_qs = tuple(Translation.objects.filter(
    # source_word__word='accidenté').all())

    # trans_1 = translation_qs[0]
    # trans_2 = translation_qs[1]
    # print(trans_1.source_word, trans_2.source_word)
    # print(trans_1.source_word == trans_2.source_word)

    # print(trans_1.target_word, trans_2.target_word)
    # print(trans_1.target_word == trans_2.target_word)

    # print(type(trans_1.part_of_speech), type(trans_2.part_of_speech))
    # print(trans_1.part_of_speech == trans_2.part_of_speech)

    # print(type(trans_1.definition), type(trans_2.definition))
    # print(trans_1.definition == trans_2.definition)

    # print(type(trans_1.prefix), type(trans_2.prefix))
    # print(trans_1.prefix == trans_2.prefix)

    # Check code
    # eng_word = Word.objects.get(word='adopt')
    # load_from_api(eng_word)

    # target_word = 'harem'
    # english_words = english_words_qs.all()
    # start_index = list(english_words.values_list(
    #     'word', flat=True)).index(target_word)

    # for word in english_words[start_index:]:
    #     load_from_api(word)

    # # Start French translate
    # create_translation(french_words_qs, french_lang, russian_lang)

    # # Start Spanish translate
    # create_translation(spanish_words_qs, spanish_lang, russian_lang)

    # Irregular verbs load
    # from dictionary.models import IrregularEnglishVerb as old_english_verb, FrenchVerb as old_french_verb
    # from dictionary.models import NewEnglishVerb, NewFrenchVerb

    # old_english_verbs_qs = old_english_verb.objects
    # old_french_verbs_qs = old_french_verb.objects

    # For english
    # for verb in old_english_verbs_qs.all():
    #     word = verb.infinitive.word
    #     new_word_qs = Word.objects.filter(word=word)

    #     if new_word_qs.exists():
    #         new_word = new_word_qs.first()
    #     else:
    #         new_word = Word(word=word, language=english_lang)
    #         new_word.save()

    #     NewEnglishVerb(
    #         infinitive=new_word,
    #         past_simple=verb.past_simple,
    #         past_participle=verb.past_participle
    #     ).save()

    # For french
    # for verb in old_french_verbs_qs.all():
    #     word = verb.infinitive.word
    #     new_word_qs = Word.objects.filter(word=word)

    #     if new_word_qs.exists():
    #         new_word = new_word_qs.first()
    #     else:
    #         new_word = Word(word=word, language=french_lang)
    #         new_word.save()
    #     try:
    #         NewFrenchVerb(
    #             infinitive=new_word,
    #             participe_present=verb.participe_present,
    #             participe_passe=verb.participe_passe,
    #             indicatif_j=verb.indicatif_j,
    #             indicatif_tu=verb.indicatif_tu,
    #             indicatif_il=verb.indicatif_il,
    #             indicatif_nous=verb.indicatif_nous,
    #             indicatif_vous=verb.indicatif_vous,
    #             indicatif_ils=verb.indicatif_ils
    #         ).save()
    #     except IntegrityError:
    #         continue

    # Normalize russian words
    russian_words_qs = Word.objects.filter(
        word__contains='*', language=russian_lang)
    # print(russian_words_qs.count())
    normalize_russian_word(russian_words_qs)
