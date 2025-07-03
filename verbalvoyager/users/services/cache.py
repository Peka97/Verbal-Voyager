

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Prefetch

from dictionary.models import EnglishVerb, Language, Translation, Word
from event_calendar.models import Course, Lesson, LessonTask, Project, ProjectType
from exercises.models import ExerciseDialog, ExerciseIrregularEnglishVerb, ExerciseWords
from lesson_plan.models import (
    EnglishLessonMainAims,
    EnglishLessonPlan,
    EnglishLessonSubsidiaryAims,
)


VERSION = settings.CACHES['default']['OPTIONS']['VERSION']
User = get_user_model()

HOUR = 3600
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY


def get_cached_user_groups(user):
    if not user:
        return None

    CACHE_KEY = f"user_{user.id}_groups_v{VERSION}"
    return cache.get_or_set(
        CACHE_KEY,
        lambda: user.groups,
        timeout=HOUR
    )


def get_cached_courses():
    CACHE_KEY = f"global_courses_v{VERSION}"
    return cache.get_or_set(
        CACHE_KEY,
        lambda: Course.objects.all(),
        timeout=WEEK
    )

# def get_cached_user_account_teacher(user):
#     CACHE_KEY = f"user_{user.id}_lessons_v{VERSION}"
#     lessons = cache.get(CACHE_KEY)

#     if lessons is not None:
#         return lessons

#     lessons = get_cached_lessons_for_teacher(user)

#     cache.set(CACHE_KEY, lessons, 3600)
#     return lessons


def get_cached_projects_for_teacher(user):
    if not user:
        return None

    projects_cache_key = f"user_{user.id}_projects_v{VERSION}"
    return cache.get_or_set(
        projects_cache_key,
        lambda: Project.objects.filter(
            teacher_id=user).values_list('pk', flat=True),
        timeout=HOUR
    )


def get_cached_projects_for_student(user):
    if not user:
        return None

    projects_cache_key = f"user_{user.id}_projects_v{VERSION}"
    return cache.get_or_set(
        projects_cache_key,
        lambda: Project.objects.filter(
            student_id=user).values_list('pk', flat=True),
        timeout=HOUR
    )


def get_cached_lessons_for_student(user, start_date, end_date):
    if not user or not start_date or not end_date:
        return None

    CACHE_KEY = f"user_{user.id}_lessons_{start_date.year}_{start_date.month}_{end_date.month}_v{VERSION}"
    lesson_plan_prefatches = (
        Prefetch('new_vocabulary', queryset=Translation.objects.all(),),
        Prefetch('main_aims', queryset=EnglishLessonMainAims.objects.all(),),
        Prefetch('subsidiary_aims',
                 queryset=EnglishLessonSubsidiaryAims.objects.all(),)
    )
    project_types_prefatches = (
        Prefetch('types', queryset=ProjectType.objects.only('name'),),
    )

    prefatches = (
        Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),),
        Prefetch('project_id',
                 queryset=Project.objects.prefetch_related(
                     *project_types_prefatches).all()),
        Prefetch(
            'lesson_plan',
            queryset=EnglishLessonPlan.objects.prefetch_related(
                *lesson_plan_prefatches).all(),
        )
    )
    lesson_fields = (
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id'
    )
    return cache.get_or_set(
        CACHE_KEY,
        lambda: Lesson.objects.filter(
            student_id=user,
            datetime__range=(start_date, end_date)
        ).prefetch_related(
            *prefatches
        ).select_related(
            'teacher_id', 'student_id'
        ).only(*lesson_fields).order_by('datetime'),
        timeout=HOUR
    )


def get_cached_lessons_for_teacher(teacher, start_date, end_date):
    if not teacher or not start_date or not end_date:
        return None

    CACHE_KEY = f"user_{teacher.id}_lessons_{start_date.year}_{start_date.month}_{end_date.month}_v{VERSION}"
    lesson_plan_prefetches = (
        Prefetch('new_vocabulary', queryset=Translation.objects.all(),),
        Prefetch('main_aims', queryset=EnglishLessonMainAims.objects.all(),),
        Prefetch('subsidiary_aims',
                 queryset=EnglishLessonSubsidiaryAims.objects.all(),
                 ),
    )
    project_types_prefetches = (
        Prefetch('types', queryset=ProjectType.objects.only('name'),),
    )

    prefetches = (
        Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),),
        Prefetch('project_id',
                 queryset=Project.objects.prefetch_related(
                     *project_types_prefetches).all()),
        Prefetch(
            'lesson_plan',
            queryset=EnglishLessonPlan.objects.prefetch_related(
                *lesson_plan_prefetches).all(),
        )
    )
    lesson_fields = (
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id',
    )
    return cache.get_or_set(
        CACHE_KEY,
        lambda: Lesson.objects.filter(
            teacher_id=teacher.pk,
            datetime__range=(start_date, end_date)
        ).prefetch_related(*prefetches)
         .select_related('teacher_id', 'student_id')
         .only(*lesson_fields)
         .order_by('datetime'),
        timeout=HOUR
    )


# def get_cached_lessons_for_other_teacher(user, teacher_id):
#     CACHE_KEY = f"user_{user.id}_lessons_for_{teacher_id}_v{VERSION}"

#     prefatches = (
#         Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),
#                  to_attr='prefetched_tasks'),
#         Prefetch('project_id__types', queryset=ProjectType.objects.only(
#             'name').all(), to_attr='prefetched_types')
#     )
#     lesson_fields = (
#         'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
#         'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
#         'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
#         'project_id'
#     )
#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: Lesson.objects.filter(
#             teacher_id=teacher_id
#         ).prefetch_related(
#             *prefatches
#         ).select_related(
#             'teacher_id', 'project_id', 'student_id'
#         ).only(*lesson_fields).order_by('datetime'),
#         timeout=3600
#     )


def get_cached_lessons_for_other_teacher(user, teacher_id, start_date, end_date):
    if not user or not start_date or not end_date:
        return None

    CACHE_KEY = f"user_{user.id}_lessons_for_{teacher_id}_v{VERSION}"

    prefatches = (
        Prefetch('lesson_tasks', queryset=LessonTask.objects.all(),
                 to_attr='prefetched_tasks'),
        Prefetch('project_id__types', queryset=ProjectType.objects.only(
            'name').all(), to_attr='prefetched_types')
    )
    lesson_fields = (
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id'
    )
    return cache.get_or_set(
        CACHE_KEY,
        lambda: Lesson.objects.filter(
            teacher_id=teacher_id,
            datetime__range=(start_date, end_date)
        ).prefetch_related(
            *prefatches
        ).select_related(
            'teacher_id', 'project_id', 'student_id'
        ).only(*lesson_fields).order_by('datetime'),
        timeout=HOUR
    )


def get_cached_projects(user):
    if not user:
        return None

    CACHE_KEY = f"user_{user.id}_projects_v{VERSION}"

    return cache.get_or_set(
        CACHE_KEY,
        lambda: Project.objects.filter(
            students=user
        ).prefetch_related(
            Prefetch('course_id', queryset=Course.objects.only('name').all(),)
        ).only('pk', 'course_id__name'),
        timeout=HOUR
    )


# def get_cached_user_english_words(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_english_words_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=EnglishWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseEnglishWords.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


def get_cached_user_words(user):
    if not user:
        return None

    CACHE_KEY = f"user_{user.id}_exercises_exercise_words_v{VERSION}"
    prefetched_languages = Prefetch(
        'lang',
        queryset=Language.objects.all(),
        to_attr='prefetched_languages'
    )
    prefetched_words = (
        Prefetch(
            'source_word',
            queryset=Word.objects.all(),
        ),
    )
    prefetched_translations = Prefetch(
        'words',
        queryset=Translation.objects.prefetch_related(*prefetched_words).all(),
    )

    return cache.get_or_set(
        CACHE_KEY,
        lambda: ExerciseWords.objects.filter(
            student=user,
        ).prefetch_related(prefetched_translations, prefetched_languages).order_by('is_active', '-created_at').all(),
        timeout=DAY
    )


# def get_cached_user_french_words(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_french_words_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=FrenchWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseFrenchWords.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


# def get_cached_user_russian_words(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_russian_words_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=EnglishWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseRussianWords.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


# def get_cached_user_spanish_words(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_spanish_words_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=SpanishWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseSpanishWords.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


# def get_cached_user_english_irregular_verbs(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_english_irregular_verbs_v{VERSION}"
#     prefetched_english_words = Prefetch(
#         'infinitive',
#         queryset=EnglishWord.objects.all(),
#         to_attr='prefetched_word'
#     )
#     prefetched_english_verb = Prefetch(
#         'words',
#         queryset=IrregularEnglishVerb.objects.prefetch_related(
#             prefetched_english_words).all(),
#         to_attr='prefetched_words'
#     )
#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseIrregularEnglishVerb.objects.filter(
#             student=user,
#             is_active=True
#         ).prefetch_related(prefetched_english_verb).only('id', 'name', 'is_active', 'created_at', 'words__infinitive').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )

def get_cached_user_english_irregular_verbs(user):
    if not user:
        return None

    CACHE_KEY = f"user_{user.id}_exercises_exercise_english_irregular_verbs_v{VERSION}"
    prefetched_english_words = Prefetch(
        'infinitive',
        queryset=Word.objects.all(),
    )
    prefetched_english_verb = Prefetch(
        'words',
        queryset=EnglishVerb.objects.prefetch_related(
            prefetched_english_words).all(),
    )

    return cache.get_or_set(
        CACHE_KEY,
        lambda: ExerciseIrregularEnglishVerb.objects.filter(
            student=user,
            is_active=True
        ).prefetch_related(prefetched_english_verb).order_by('is_active', '-created_at').all(),
        timeout=DAY
    )


# def get_cached_user_english_dialogs(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_english_dialogs_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=EnglishWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseEnglishDialog.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


def get_cached_user_dialogs(user):
    if not user:
        return None

    CACHE_KEY = f"user_{user.id}_exercises_exercise_dialogs_v{VERSION}"
    prefetched_words = (
        Prefetch(
            'source_word',
            queryset=Word.objects.all(),
        ),
    )
    prefetched_translations = Prefetch(
        'words',
        queryset=Translation.objects.prefetch_related(*prefetched_words).all(),
    )

    return cache.get_or_set(
        CACHE_KEY,
        lambda: ExerciseDialog.objects.filter(
            student=user
        ).prefetch_related(prefetched_translations).order_by('is_active', '-created_at').all(),
        timeout=DAY
    )


# def get_cached_user_french_dialogs(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_french_dialogs_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=FrenchWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseFrenchDialog.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


# def get_cached_user_russian_dialogs(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_russian_dialogs_v{VERSION}"
#     prefetched_words = Prefetch(
#         'words',
#         queryset=EnglishWord.objects.all(),
#         to_attr='prefetched_words'
#     )

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseRussianDialog.objects.filter(
#             student=user
#         ).prefetch_related(prefetched_words).only('id', 'name', 'is_active', 'created_at').order_by('is_active', '-created_at').all(),
#         timeout=60*60*24
#     )


# def get_cached_user_spanish_dialogs(user):
#     CACHE_KEY = f"user_{user.id}_exercises_exercise_spanish_dialogs_v{VERSION}"

#     return cache.get_or_set(
#         CACHE_KEY,
#         lambda: ExerciseSpanishDialog.objects.filter(
#             student=user
#         ).prefetch_related('words').only('id', 'name', 'is_active', 'created_at').all(),
#         timeout=60*60*24
#     )


def get_cached_all_teachers():
    CACHE_KEY = f'global_users_in_group_teachers_v{VERSION}'
    return cache.get_or_set(
        CACHE_KEY,
        lambda: User.objects.filter(groups__name='Teacher').exclude(
            username='admin').values_list('pk', flat=True),
        timeout=HOUR
    )


def get_cached_admin_user_in_group(group_name):
    if not group_name:
        return None

    CACHE_KEY = f'global_admin_users_in_group_{group_name}_v{VERSION}'
    return cache.get_or_set(
        CACHE_KEY,
        lambda: User.objects.filter(
            groups__name=group_name).order_by('last_name', 'first_name'),
        timeout=HOUR
    )
