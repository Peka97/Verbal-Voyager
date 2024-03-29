from django.contrib import admin
from .models import Course, Review, ProjectType, Project


admin.site.register(Course)
admin.site.register(Review)
admin.site.register(ProjectType)
admin.site.register(Project)
