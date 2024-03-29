from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def is_teacher(self):
        try:
            return True if self.groups.filter(name='Teacher').exists() else False
        except ValueError:
            return False
