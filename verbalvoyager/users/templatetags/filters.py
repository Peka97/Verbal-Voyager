import pytz
from datetime import datetime, timedelta

from logger import get_logger
from django import template
from django.conf import settings


register = template.Library()

logger = get_logger()

# Old
# @register.filter(name="type_names_to_list")
# def type_names_to_list(value):
#     return [proj_type.name for proj_type in value]
@register.filter(name="type_names_to_list")
def type_names_to_list(project):
    # Проверяем, есть ли предзагруженные типы
    if hasattr(project, 'prefetched_types'):
        return [t.name for t in project.prefetched_types]
    # Fallback для случая без prefetch
    return list(project.types.values_list('name', flat=True))


@register.filter(name="join_student_names")
def join_student_names(value):
    try:
        return ", ".join(
            [
                f"{lesson.student_id.last_name} {lesson.student_id.first_name}"
                for lesson in value
            ]
        )
    except AttributeError:
        logger.error(value)
        return ", ".join(
            [
                f"{lesson.student_id}"
                for lesson in value
            ]
        )


@register.filter(name="time")
def time(value):
    return f"{value.hour:02}:{value.minute:02}"


@register.filter(name="teacher_warn_lesson")
def teacher_warn_lesson(lesson):
    tz_server = pytz.timezone(settings.TIME_ZONE)
    tz_user = pytz.timezone(lesson.teacher_id.timezone)
    user_lesson_datetime = lesson.datetime.astimezone(tz_user)

    # Урок оплачен, но отменён.
    if lesson.is_paid and lesson.status in ('C',):
        return True

    # Урок не оплачен, до урока меньше суток.
    if not lesson.is_paid and (user_lesson_datetime + timedelta(days=1)) >= datetime.today().astimezone(tz_server):
        return True


@register.filter(name="teacher_dang_lesson")
def teacher_dang_lesson(lesson):
    tz_server = pytz.timezone(settings.TIME_ZONE)
    tz_user = pytz.timezone(lesson.teacher_id.timezone)
    user_lesson_datetime = lesson.datetime.astimezone(tz_user)

    # Урок не оплачен и проведён.
    if not lesson.is_paid and lesson.status in ('D',):
        return True

    # Урок не оплачен, до урока меньше 2-х часов.
    if not lesson.is_paid and (user_lesson_datetime + timedelta(hours=2)) >= datetime.today().astimezone(tz_server):
        return True


@register.filter(name="student_warn_lesson")
def student_warn_lesson(lesson):
    tz_server = pytz.timezone(settings.TIME_ZONE)
    tz_user = pytz.timezone(lesson.teacher_id.timezone)
    user_lesson_datetime = lesson.datetime.astimezone(tz_user)

    # Урок оплачен, но отменён.
    if lesson.is_paid and lesson.status in ('C',):
        return True

    # Урок не оплачен, до урока меньше суток.
    if not lesson.is_paid and lesson.status in ('P', ) and (user_lesson_datetime - timedelta(days=1)) <= datetime.today().astimezone(tz_server):
        return True

    # Урок оплачен, запланированное время прошло, но статус не завершён или отменён.
    if lesson.is_paid and user_lesson_datetime <= datetime.today().astimezone(tz_server) and lesson.status not in ('D', 'C'):
        return True


@register.filter(name="student_dang_lesson")
def student_dang_lesson(lesson):
    tz_server = pytz.timezone(settings.TIME_ZONE)
    tz_user = pytz.timezone(lesson.teacher_id.timezone)
    user_lesson_datetime = lesson.datetime.astimezone(tz_user)

    # Урок не оплачен и проведён.
    if not lesson.is_paid and lesson.status in ('D',):
        return True

    # Урок не оплачен, до урока меньше 2-х часов.
    if not lesson.is_paid and lesson.status in ('P', ) and (user_lesson_datetime - timedelta(hours=2)) <= datetime.today().astimezone(tz_server):
        return True


@register.filter(name="datetime_plus_duration")
def datetime_plus_duration(lesson_datetime, duration):
    time_end = lesson_datetime + timedelta(minutes=duration)
    return f"{lesson_datetime.strftime('%H:%M')} - {time_end.strftime('%H:%M')}"
