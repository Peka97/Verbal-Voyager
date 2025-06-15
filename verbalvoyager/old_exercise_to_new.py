def transfer_exercise_words(qs, source_lang, target_lang):
    for old_exercise in qs.all():
        translations = []

        for word in old_exercise.words.all():
            print(f"SEARCH WORD: {word.word} - {word.translation}")

            if len(word.translation.split(', ')) > 1:
                search_translation = word.translation.split(', ')[0]
            else:
                search_translation = word.translation

            new_translation_qs = Translation.objects.filter(
                Q(source_word__language=source_lang) &
                Q(source_word__word=word.word) &
                Q(target_word__word=search_translation)
            )
            new_translation = new_translation_qs.first()

            if not new_translation_qs.exists():
                print(f"NOT FOUND WORD: {word.word}. Creating...")

                new_source_word_qs = Word.objects.filter(
                    word=word.word, language=source_lang)

                if new_source_word_qs.exists():
                    new_source_word = new_source_word_qs.first()
                else:
                    new_source_word = Word(
                        word=word.word,
                        language=source_lang
                    )
                    new_source_word.save()

                new_target_word_qs = Word.objects.filter(
                    word=search_translation, language=target_lang)

                if new_target_word_qs.exists():
                    new_target_word = new_target_word_qs.first()
                else:
                    new_target_word = Word(
                        word=search_translation,
                        language=target_lang
                    )
                    new_target_word.save()

                new_translation = Translation(
                    source_word=new_source_word,
                    target_word=new_target_word
                )
                try:
                    new_translation.save()
                except IntegrityError:
                    print(f"TRANSLATION ALREADY EXISTS: {new_translation}")
                    continue

            translations.append(new_translation)
        # old_words_list = '\n'.join(
        #     [word.word + ' - ' + word.translation for word in old_exercise.words.all()]
        # )
        # print()
        # print(
        #     f"OLD WORDS:\n" + old_words_list
        # )
        # translations_list = '\n'.join(
        #     [translation.source_word.word + ' - ' +
        #         translation.target_word.word for translation in translations]
        # )
        # print()

        # print(
        #     f"NEW WORDS:\n" + translations_list
        # )

        new_exercise = ExerciseWords(
            name=old_exercise.name,
            category=old_exercise.category,
            is_active=old_exercise.is_active,
            external_access=old_exercise.external_access,
            teacher=old_exercise.teacher,
            student=old_exercise.student,
            lang=source_lang
        )
        new_exercise.save()
        new_exercise.words.set(translations)
        new_exercise.save()
        print("NEW EXERCISE CREATED.")
        # break


def transfer_exercise_dialogs(qs, source_lang, target_lang):
    for old_exercise in qs.all():
        translations = []

        for word in old_exercise.words.all():
            print(f"SEARCH WORD: {word.word} - {word.translation}")

            if len(word.translation.split(', ')) > 1:
                search_translation = word.translation.split(', ')[0]
            else:
                search_translation = word.translation

            new_translation_qs = Translation.objects.filter(
                Q(source_word__language=source_lang) &
                Q(source_word__word=word.word) &
                Q(target_word__word=search_translation)
            )
            new_translation = new_translation_qs.first()

            if not new_translation_qs.exists():
                print(f"NOT FOUND WORD: {word.word}. Creating...")

                new_source_word_qs = Word.objects.filter(
                    word=word.word, language=source_lang)

                if new_source_word_qs.exists():
                    new_source_word = new_source_word_qs.first()
                else:
                    new_source_word = Word(
                        word=word.word,
                        language=source_lang
                    )
                    new_source_word.save()

                new_target_word_qs = Word.objects.filter(
                    word=search_translation, language=target_lang)

                if new_target_word_qs.exists():
                    new_target_word = new_target_word_qs.first()
                else:
                    new_target_word = Word(
                        word=search_translation,
                        language=target_lang
                    )
                    new_target_word.save()

                new_translation = Translation(
                    source_word=new_source_word,
                    target_word=new_target_word
                )
                try:
                    new_translation.save()
                except IntegrityError:
                    print(f"TRANSLATION ALREADY EXISTS: {new_translation}")
                    continue

            translations.append(new_translation)
        # old_words_list = '\n'.join(
        #     [word.word + ' - ' + word.translation for word in old_exercise.words.all()]
        # )
        # print()
        # print(
        #     f"OLD WORDS:\n" + old_words_list
        # )
        # translations_list = '\n'.join(
        #     [translation.source_word.word + ' - ' +
        #         translation.target_word.word for translation in translations]
        # )
        # print()

        # print(
        #     f"NEW WORDS:\n" + translations_list
        # )

        new_exercise = ExerciseDialog(
            name=old_exercise.name,
            category=old_exercise.category,
            text=old_exercise.text,
            is_active=old_exercise.is_active,
            external_access=old_exercise.external_access,
            teacher=old_exercise.teacher,
            student=old_exercise.student,
            lang=source_lang
        )
        new_exercise.save()
        new_exercise.words.set(translations)
        new_exercise.save()
        print("NEW EXERCISE CREATED.")
        # break


def transfer_irregular_verbs(qs, source_lang, target_lang):
    for old_exercise in qs.all():
        if old_exercise.pk < 14:
            continue
        english_verbs = []

        for irregular_verb in old_exercise.words.all():
            print(
                f"SEARCH VERB: {irregular_verb.infinitive.word}")

            new_english_verb_qs = NewEnglishVerb.objects.filter(
                infinitive__word=irregular_verb.infinitive.word
            )

            if not new_english_verb_qs.exists():
                print(
                    f"NOT FOUND WORD: {irregular_verb.infinitive.word}. Creating...")
                english_verb = Word.objects.get(word='can')

                new_english_verb = NewEnglishVerb(
                    infinitive=english_verb,
                    past_simple=irregular_verb.past_simple,
                    past_participle=irregular_verb.past_participle
                )
                new_english_verb.save()
            else:
                new_english_verb = new_english_verb_qs.first()

            english_verbs.append(new_english_verb)

        new_exercise = NewExerciseIrregularEnglishVerb(
            name=old_exercise.name,
            category=old_exercise.category,
            is_active=old_exercise.is_active,
            external_access=old_exercise.external_access,
            teacher=old_exercise.teacher,
            student=old_exercise.student,
        )
        new_exercise.save()
        new_exercise.words.set(english_verbs)
        new_exercise.save()
        print("NEW EXERCISE CREATED.")
        # break


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verbalvoyager.settings')
    django.setup()
    from django.db.utils import IntegrityError

    # Old models
    from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseSpanishWords
    from exercises.models import ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseSpanishDialog
    from exercises.models import ExerciseIrregularEnglishVerb

    # New models
    from exercises.models import ExerciseWords, ExerciseDialog, NewExerciseIrregularEnglishVerb

    from dictionary.models import Translation, Word, Language, IrregularEnglishVerb, NewEnglishVerb
    from django.db.models import Q

    # Transfer old exercises to new exercises
    en_lang = Language.objects.get(name='English')
    fr_lang = Language.objects.get(name='French')
    sp_lang = Language.objects.get(name='Spanish')
    ru_lang = Language.objects.get(name='Russian')

    # Words
    old_english_exercises_qs = ExerciseEnglishWords.objects
    old_french_exercises_qs = ExerciseFrenchWords.objects
    old_spanish_exercises_qs = ExerciseSpanishWords.objects

    # transfer_exercise_words(old_english_exercises_qs, en_lang, ru_lang)
    # transfer_exercise_words(old_french_exercises_qs, fr_lang, ru_lang)
    # transfer_exercise_words(old_spanish_exercises_qs, sp_lang, ru_lang)

    # Dialogs
    old_english_exercises_qs = ExerciseEnglishDialog.objects
    old_french_exercises_qs = ExerciseFrenchDialog.objects
    old_spanish_exercises_qs = ExerciseSpanishDialog.objects

    # transfer_exercise_dialogs(old_english_exercises_qs, en_lang, ru_lang)
    # transfer_exercise_dialogs(old_french_exercises_qs, fr_lang, ru_lang)
    # transfer_exercise_dialogs(old_spanish_exercises_qs, sp_lang, ru_lang)

    # Irregular verbs
    old_english_exercises_qs = ExerciseIrregularEnglishVerb.objects

    transfer_irregular_verbs(old_english_exercises_qs, en_lang, ru_lang)
