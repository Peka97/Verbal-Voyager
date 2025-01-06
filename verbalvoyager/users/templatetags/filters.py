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