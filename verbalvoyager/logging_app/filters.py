from django.utils.translation import gettext_lazy as _

from exercises.filters import AbstractUserListFilter


class TeachersListFilter(AbstractUserListFilter):
    title = _("Учитель")
    parameter_name = "teacher"
    user_group = 'Teacher'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user=self.value())
