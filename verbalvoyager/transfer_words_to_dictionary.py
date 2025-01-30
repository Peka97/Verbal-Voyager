import os

import django
from django.db import transaction

# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()



if __name__ == '__main__':
    from exercises.models import Word, ExerciseWords, ExerciseEnglishWords, ExerciseWordsResult
    from dictionary.models import EnglishWord as eng_word, FrenchWord as fr_word
    from exercise_result.models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult
    
    words = Word.objects
    exercises = ExerciseWords.objects.all()
    results = ExerciseWordsResult.objects.all()
    with transaction.atomic():
        eng_word.objects.bulk_create(words.filter(lang='eng').all)
        
        fr_word.objects.bulk_create(words.filter(lang='fr').all)
        
        ExerciseEnglishWords.objects.bulk_update(exercises, ('words',))
        for exercise in exercises:
            new_exercise = ExerciseEnglishWords.objects.get(pk=exercise.pk)
            new_exercise.words.set(exercise.words.all())
        
        ExerciseEnglishWordsResult.objects.bulk_create(results)
    
        
        
    
    # with transaction.atomic():
    #     ExerciseEnglishWords.objects.bulk_update(exercises, ('words',))
    # for exercise in exercises:
    #     new_exercise = ExerciseEnglishWords.objects.get(pk=exercise.pk)
    #     new_exercise.words.set(exercise.words.all())
        
    
    # results = ExerciseWordsResult.objects.all()
    # with transaction.atomic():
    #     ExerciseEnglishWordsResult.objects.bulk_create(results)