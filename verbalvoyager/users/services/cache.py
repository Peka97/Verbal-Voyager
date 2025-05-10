from itertools import chain


from django.core.cache import cache
from django.db.models import Prefetch

from exercises.models import ExerciseEnglishWords, ExerciseFrenchWords, ExerciseRussianWords, ExerciseEnglishDialog, ExerciseFrenchDialog, ExerciseIrregularEnglishVerb, ExerciseSpanishWords, ExerciseRussianDialog, ExerciseSpanishDialog
from event_calendar.models import Lesson, LessonTask, Project, Course, ProjectType


# def user_cache(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         CACHE_KEY_PREFIX = f"user_{request.user.id}_{request.path}"
#         return cache_page(
#             60 * 15,
#             key_prefix=CACHE_KEY_PREFIX
#         )(view_func)(request, *args, **kwargs)
#     return _wrapped_view

# def session_cache(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         CACHE_KEY_PREFIX = f"user_{request.session.session_key}_{request.path}"
#         return cache_page(
#             60 * 15,
#             key_prefix=CACHE_KEY_PREFIX
#         )(view_func)(request, *args, **kwargs)
#     return _wrapped_view

def get_cached_courses(user):
    cache_key = f"user_{user.id}_courses_v2"
    courses = cache.get_or_set(
        cache_key,
        lambda: tuple(Course.objects.all()),
        timeout=60*60*24*7
    )
    return courses

def get_cached_user_account_teacher(user):
    cache_key = f"user_{user.id}_lessons_v2"
    lessons = cache.get(cache_key)
    
    if lessons is not None:
        return lessons

    projects_cache_key = f"user_{user.id}_projects"
    project_ids = cache.get_or_set(
        projects_cache_key,
        lambda: tuple(Project.objects.filter(teacher_id=user).values_list('pk', flat=True)),
        3600
    )

    project_types_prefetch = Prefetch(
        'types',
        queryset=cache.get_or_set(
            'all_project_types',
            lambda: ProjectType.objects.only('name'),
            86400
        ),
        to_attr='prefetched_types'
    )

    lessons = list(Lesson.objects.filter(
        teacher_id=user
    ).prefetch_related(
        'lesson_tasks',
        Prefetch(
            'project_id',
            queryset=Project.objects.filter(id__in=project_ids)
                      .prefetch_related(project_types_prefetch)
                      .only('id'),
            to_attr='prefetched_project'
        )
    ).select_related(
        'teacher_id', 'student_id', 'project_id'
    ).only(
        'id', 'title', 'datetime', 'duration', 'is_paid', 'status',
        'teacher_id__first_name', 'teacher_id__last_name', 'teacher_id__timezone',
        'student_id__first_name', 'student_id__last_name', 'student_id__timezone',
        'project_id',
    ).order_by('datetime'))

    cache.set(cache_key, lessons, 1800)
    return lessons

def get_cached_lessons(user):
    cache_key = f"user_{user.id}_lessons_v3"
    lessons = cache.get(cache_key)
    
    if lessons:
        return lessons

    lessons = tuple(Lesson.objects.filter(
        student_id=user
    ).prefetch_related(
        Prefetch('lesson_tasks', queryset=LessonTask.objects.only('id', 'name')),
        Prefetch('project_id__types', queryset=ProjectType.objects.only('name'))
    ).select_related(
        'teacher_id', 'project_id', 'student_id'
    ).order_by('datetime'))

    cache.set(cache_key, lessons, timeout=60*30)
    return lessons

def get_cached_projects(user):
    cache_key = f"user_{user.id}_projects_v3"
    projects = cache.get(cache_key)
    
    if projects:
        return projects
    
    projects = tuple(Project.objects.filter(
            students=user
        ).prefetch_related(
            Prefetch('course_id', queryset=Course.objects.only('name'),)
        ).only('pk', 'course_id__name'))
    cache.set(cache_key, projects, 1800)
    return projects

def get_cached_english_words(user):
    cache_key = f"user_{user.id}_english_words_v4"

    words = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseEnglishWords.objects.filter(
            student=user
        )),
        timeout=60*60*24
    )
    return words

def get_cached_french_words(user):
    cache_key = f"user_{user.id}_french_words_v2"
    words = cache.get(cache_key)
    
    if words:
        return words

    words = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseFrenchWords.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return words

def get_cached_russian_words(user):
    cache_key = f"user_{user.id}_russian_words_v2"
    words = cache.get(cache_key)
    
    if words:
        return words

    words = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseRussianWords.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return words

def get_cached_spanish_words(user):
    cache_key = f"user_{user.id}_spanish_words_v2"
    words = cache.get(cache_key)
    
    if words:
        return words

    words = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseSpanishWords.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return words
    

def get_cached_english_irregular_verbs(user):
    cache_key = f"user_{user.id}_english_irregular_verbs_v2"
    return cache.get_or_set(
        cache_key,
        lambda: list(ExerciseIrregularEnglishVerb.objects.filter(
            student=user,
            is_active=True
        ).only('id', 'name')),
        timeout=60*60*24
    )

def get_cached_english_dialogs(user):
    cache_key = f"user_{user.id}_english_dialogs_v2"
    dialogs = cache.get(cache_key)
    
    if dialogs:
        return dialogs
    
    dialogs = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseEnglishDialog.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return dialogs

def get_cached_french_dialogs(user):
    cache_key = f"user_{user.id}_french_dialogs_v2"
    dialogs = cache.get(cache_key)
    
    if dialogs:
        return dialogs
    
    dialogs = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseFrenchDialog.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return dialogs

def get_cached_russian_dialogs(user):
    cache_key = f"user_{user.id}_russian_dialogs_v2"
    dialogs = cache.get(cache_key)
    
    if dialogs:
        return dialogs
    
    dialogs = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseRussianDialog.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return dialogs

def get_cached_spanish_dialogs(user):
    cache_key = f"user_{user.id}_spanish_dialogs_v2"
    dialogs = cache.get(cache_key)
    
    if dialogs:
        return dialogs
    
    dialogs = cache.get_or_set(
        cache_key,
        lambda: tuple(ExerciseSpanishDialog.objects.filter(
            student=user
        ).only('id', 'name')),
        timeout=60*60*24
    )
    return dialogs
    