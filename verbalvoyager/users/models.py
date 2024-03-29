from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    def is_teacher(self):
        try:
            return True if self.groups.filter(name='Teacher').exists() else False
        except ValueError:
            return False

    def is_admin(self):
        try:
            return True if self.username == 'admin' else False
        except ObjectDoesNotExist:
            return False
