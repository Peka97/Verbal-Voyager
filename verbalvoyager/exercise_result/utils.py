import logging

from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseRussianWords, ExerciseSpanishWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseSpanishDialog, ExerciseRussianDialog, ExerciseIrregularEnglishVerb # noqa 
from exercise_result.models import ExerciseEnglishWordsResult, ExerciseFrenchWordsResult, ExerciseRussianWordsResult, ExerciseSpanishWordsResult, ExerciseEnglishDialogResult, ExerciseFrenchDialogResult, ExerciseSpanishDialogResult, ExerciseRussianDialogResult, ExerciseIrregularEnglishVerbResult # noqa 


logger = logging.getLogger('django')

def get_exercise_class_name(ex_type: str, ex_lang: str) -> tuple:
    ex_type =  ''.join(map(lambda word: word.capitalize(), ex_type.split("_")))
    exercise_obj_name = f"Exercise{ex_lang.capitalize()}{ex_type}"
    exercise_result_obj_name = exercise_obj_name + 'Result'
    return globals().get(exercise_obj_name), globals().get(exercise_result_obj_name)