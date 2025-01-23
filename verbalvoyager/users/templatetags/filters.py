from datetime import datetime, timedelta

from django import template

register = template.Library()


@register.filter(name="type_names_to_list")
def type_names_to_list(value):
    return [proj_type.name for proj_type in value]


@register.filter(name="join_student_names")
def join_student_names(value):
    return ", ".join(
        [
            f"{lesson.student_id.last_name} {lesson.student_id.first_name}"
            for lesson in value
        ]
    )


@register.filter(name="time")
def time(value):
    return f"{value.hour:02}:{value.minute:02}"


@register.filter(name="teacher_warn_lesson")
def teacher_warn_lesson(lesson):
    # Урок оплачен, но отменён.
    if lesson.is_paid and lesson.status in ('C',):
        return True

    # Урок не оплачен, до урока меньше суток.
    if not lesson.is_paid and (lesson.datetime + timedelta(days=1)) >= datetime.today():
        return True

    # Урок оплачен, запланированное время прошло, но статус не завершён или отменён.
    # if lesson.is_paid and lesson.datetime >= datetime.today() and lesson.status not in ('D', 'C'):
    #     return True


@register.filter(name="teacher_dang_lesson")
def teacher_dang_lesson(lesson):
    # Урок не оплачен и проведён.
    if not lesson.is_paid and lesson.status in ('D',):
        return True

    # Урок не оплачен, до урока меньше 2-х часов.
    if not lesson.is_paid and (lesson.datetime + timedelta(hours=2)) >= datetime.today():
        return True


@register.filter(name="student_warn_lesson")
def student_warn_lesson(lesson):
    # Урок оплачен, но отменён.
    if lesson.is_paid and lesson.status in ('C',):
        return True

    # Урок не оплачен, до урока меньше суток.
    if not lesson.is_paid and lesson.status in ('P', ) and (lesson.datetime - timedelta(days=1)) <= datetime.today():
        return True

    # Урок оплачен, запланированное время прошло, но статус не завершён или отменён.
    # if lesson.is_paid and lesson.datetime >= datetime.today() and lesson.status not in ('D', 'C'):
    #     return True


@register.filter(name="student_dang_lesson")
def student_dang_lesson(lesson):
    # Урок не оплачен и проведён.
    if not lesson.is_paid and lesson.status in ('D',):
        return True

    # Урок не оплачен, до урока меньше 2-х часов.
    if not lesson.is_paid and lesson.status in ('P', ) and (lesson.datetime - timedelta(hours=2)) <= datetime.today():
        return True
