import os

import django
from django.db import transaction

# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()



if __name__ == '__main__':
    # Old
    from exercises.models import Word, ExerciseWords, ExerciseDialog, ExerciseWordsResult
    # New
    from exercises.models import  ExerciseEnglishWords, ExerciseEnglishDialog
    from dictionary.models import EnglishWord as eng_word, FrenchWord as fr_word
    from exercise_result.models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult
    
    words = Word.objects
    exercises = ExerciseWords.objects.all()
    results = ExerciseWordsResult.objects.all()
    dialogs = ExerciseDialog.objects.all()
        
    with transaction.atomic():
        eng_word.objects.bulk_create(words.filter(lang='eng').all)
        
        fr_word.objects.bulk_create(words.filter(lang='fr').all)
        
        ExerciseEnglishWords.objects.bulk_update(exercises, ('words',))
        for exercise in exercises:
            new_exercise = ExerciseEnglishWords.objects.get(pk=exercise.pk)
            new_exercise.words.set(exercise.words.all())
            
        ExerciseEnglishDialog.objects.bulk_create(dialogs)
        for dialog in dialogs:
            new_dialog = ExerciseEnglishDialog.objects.get(pk=dialog.pk)
            new_dialog.words.set(dialog.words.all())
        
        ExerciseEnglishWordsResult.objects.bulk_create(results)
