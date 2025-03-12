def get_words_learned_count(*args):
    count = 0

    for exercise_type in args:
        queryset = exercise_type.filter(is_active=False).prefetch_related(
            'words').all()

        for exercise in queryset:
            count += exercise.words.count()

    return count


def get_exercises_done_count(*args):
    count = 0

    for exercise_type in args:
        count += exercise_type.filter(is_active=False).count()

    return count
