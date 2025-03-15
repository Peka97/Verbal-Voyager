from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldError

from pages.filters import DROPDOWN_TEMPLATE_PATH

User = get_user_model()


class AbstractUserListFilter(SimpleListFilter):
    template = DROPDOWN_TEMPLATE_PATH
    user_group: str
    user_field_name: str

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        users = User.objects.filter(
            groups__name=self.user_group).order_by('last_name', 'first_name')

        return [
            (user.pk, _(f'{user.last_name} {user.first_name}')) for user in users
        ]


class TeachersListFilter(AbstractUserListFilter):
    title = _("Учитель")
    parameter_name = "teacher"
    user_group = 'Teacher'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(exercise__teacher=self.value())


class StudentsListFilter(AbstractUserListFilter):
    title = _("Ученик")
    parameter_name = "student"
    user_group = 'Student'

    def queryset(self, request, queryset):
        return queryset.filter(exercise__student=self.value()) if self.value() else None
