from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    def is_teacher(self):
        try:
            return True if self.groups.filter(name='Teacher').exists() else False
        except ValueError:
            return False

    def is_student(self):
        try:
            return True if self.groups.filter(name='Student').exists() else False
        except ValueError:
            return False

    def is_admin(self):
        try:
            return True if self.username == 'admin' else False
        except ObjectDoesNotExist:
            return False

    def get_teachers(self):
        return self.objects.filter(groups__name__in=['Teacher'])
        # teachers = [user for user in self.objects.all() if user.is_teacher]
        # return teachers

    def get_students(self):
        return self.objects.filter(groups__name__in=['Student'])
        # students = [user for user in self.objects.all() if user.is_student]
        # return students
