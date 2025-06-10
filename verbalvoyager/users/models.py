from typing import Any

import pytz
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.core.cache import cache


# from .services.cache import get_cached_user_groups


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

    def _in_group(self, group_name):
        cache_key = f"user_{self.pk}_in_group_{group_name.lower()}"
        return cache.get_or_set(
            cache_key,
            lambda: self.groups.filter(name=group_name).exists(),
            timeout=3600
        )

    def is_teacher(self):
        return self._in_group('Teacher') if not isinstance(self, AnonymousUser) else False

    def is_student(self):
        return self._in_group('Student') if not isinstance(self, AnonymousUser) else False

    def is_supervisor(self):
        return self._in_group('Supervisor') if not isinstance(self, AnonymousUser) else False

    # def is_admin(self):
    #     return self.is_superuser if not isinstance(self, AnonymousUser) else False

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
