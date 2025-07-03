import logging

from exercise_result.models import (
    ExerciseDialogResult,
    ExerciseIrregularEnglishVerbResult,
    ExerciseWordsResult,
)
from exercises.models import ExerciseDialog, ExerciseIrregularEnglishVerb, ExerciseWords


logger = logging.getLogger('django')


def get_exercise_and_result_class(ex_type: str) -> object | None:
    match ex_type:
        case 'words':
            return ExerciseWords, ExerciseWordsResult
        case 'dialog':
            return ExerciseDialog, ExerciseDialogResult
        case 'irregular_verbs':
            return ExerciseIrregularEnglishVerb, ExerciseIrregularEnglishVerbResult
        case _:
            return None, None


def get_last_step(ex_type: str) -> str | None:
    match ex_type:
        case 'words':
            return '5'
        case 'dialog':
            return '1'
        case 'irregular_verbs':
            return '3'
        case _:
            return None
