
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from exercises.models import ExerciseEnglishWords, ExerciseEnglishDialog, ExerciseIrregularEnglishVerb

User = get_user_model()


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


def init_student_demo_access(user: User):
    student_demo_group, _ = Group.objects.get_or_create(name='StudentDemo')
    user.groups.add(student_demo_group.id)
    create_demo_exercise(ExerciseEnglishWords, user.id)
    create_demo_exercise(ExerciseIrregularEnglishVerb, user.id)
    create_demo_exercise(ExerciseEnglishDialog, user.id)


def create_demo_exercise(exercise_model, user_id):
    demo_exercise = exercise_model.objects.filter(
        category__name='Demo'
    ).first()
    words = tuple(demo_exercise.words.all())
    teacher_demo_group, _ = Group.objects.get_or_create(name='TeacherDemo')
    teacher_id = User.objects.filter(
        groups__name=teacher_demo_group.name).first().id
    exercise = exercise_model(
        student_id=user_id,
        teacher_id=teacher_id,
        is_active=True,
        name=f'Demo {exercise_model.__name__}'
    )

    if exercise_model is ExerciseEnglishDialog:
        exercise.text = demo_exercise.text

    exercise.save()
    exercise.words.set(words)
