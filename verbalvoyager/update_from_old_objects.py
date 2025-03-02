import os
import django
from django.forms.models import model_to_dict

if __name__ == '__main__':
    # Django setup
    os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
    django.setup()

    from exercises.models import EnglishWord, FrenchWord, ExerciseWords, ExerciseDialog

    from dictionary.models import EnglishWord as new_EnglishWord, FrenchWord as new_FrenchWord
    from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseEnglishDialog, ExerciseFrenchDialog
    from users.models import User

    # Words
    # old_objects = EnglishWord.objects.all()
    # new_model = new_EnglishWord

    # for word in old_objects:
    #     new_word = new_EnglishWord.objects.filter(
    #         word=word.word, translation=word.translate)

    #     if not new_word.exists():
    #         new_word_obj = new_EnglishWord(
    #             word=word.word, translation=word.translate)
    #         new_word_obj.save()
    #         print(f'[CREATED] {new_word_obj}')
    #     print(f'[SKIP] {word}')

    # Exercises
    old_objects = ExerciseWords.objects.filter(student__pk='17').all()
    new_model = ExerciseFrenchWords
    new_model.objects.all().delete()

    for exercise in old_objects:
        new_words = []
        words = exercise.words.all()

        for word in words:
            word_in_new_model = new_FrenchWord.objects.filter(
                word=word.word, translation=word.translate)

            if word_in_new_model.exists():
                print(word_in_new_model)
                new_words.append(word_in_new_model.first())
            else:
                print(f'[NOT FOUND] {word}')
                new_words = []
                break

        if new_words:

            new_exercise_dict = model_to_dict(exercise)
            del new_exercise_dict['id']
            del new_exercise_dict['words']
            new_exercise_dict['student'] = User.objects.get(
                pk=new_exercise_dict['student'])
            new_exercise_dict['teacher'] = User.objects.get(
                pk=new_exercise_dict['teacher'])

            new_exercise = new_model.objects.create(**new_exercise_dict)
            new_exercise.words.set(new_words)
            new_exercise.save()
            print(f"[CREATED] {new_exercise}")
