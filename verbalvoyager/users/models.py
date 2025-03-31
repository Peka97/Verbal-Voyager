from typing import Any

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class User(AbstractUser):
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default='Europe/Saratov',
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._meta.get_field('email').__dict__['_unique'] = True
        self._meta.get_field('email').__dict__['null'] = True

    def is_teacher(self):
        try:
            return self.groups.filter(name='Teacher').exists()
        except ValueError:
            return False

    def is_student(self):
        try:
            return self.groups.filter(name='Student').exists()
        except ValueError:
            return False

    def is_supervisor(self):
        try:
            return self.groups.filter(name='Supervisor').exists()
        except ValueError:
            return False

    def is_admin(self):
        try:
            return True if self.username == 'admin' else False
        except ObjectDoesNotExist:
            return False

    def get_groups(self):
        return tuple(self.groups.all())

    get_groups.short_description = 'Группы пользователя'

    def get_teachers(self):
        return self.objects.filter(groups__name__in=['Teacher'])

    def get_students(self):
        return self.objects.filter(groups__name__in=['Student'])

    def __str__(self):
        if self.last_name and self.first_name:
            return f'{self.last_name} {self.first_name}'

        return self.username
