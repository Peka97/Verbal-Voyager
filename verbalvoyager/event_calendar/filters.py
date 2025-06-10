from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldError

from pages.filters import DROPDOWN_TEMPLATE_PATH
from users.services.cache import get_cached_admin_user_in_group


User = get_user_model()


class AbstractUserListFilter(SimpleListFilter):
    template = DROPDOWN_TEMPLATE_PATH
    user_group: str
    user_field_name: str

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        users = get_cached_admin_user_in_group(self.user_group)

        return [
            (user.pk, _(f'{user.last_name} {user.first_name}')) for user in users
        ]


class TeachersListFilter(AbstractUserListFilter):
    title = _("Учитель")
    parameter_name = "teacher"
    user_group = 'Teacher'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(teacher_id=self.value())


class StudentsListFilter(AbstractUserListFilter):
    title = _("Ученик")
    parameter_name = "student"
    user_group = 'Student'

    def queryset(self, request, queryset):
        try:
            return queryset.filter(students=self.value()) if self.value() else None
        except FieldError:
            return queryset.filter(student_id=self.value()) if self.value() else None
