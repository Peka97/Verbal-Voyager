from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
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

    def is_admin(self):
        try:
            return True if self.username == 'admin' else False
        except ObjectDoesNotExist:
            return False

    def get_teachers(self):
        return self.objects.filter(groups__name__in=['Teacher'])

    def get_students(self):
        return self.objects.filter(groups__name__in=['Student'])
