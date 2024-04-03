from django.contrib import admin

from .models import Lesson
from .forms import LessonAdminForm


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    filter_horizontal = ('students', )
    list_display = ('pk', 'teacher', 'get_students', 'title')
    save_as = True
