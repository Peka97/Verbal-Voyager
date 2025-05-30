import os
import urllib.parse

from django.db import models
from django.core.files.storage import FileSystemStorage


def document_upload_to(instance, filename):
    return os.path.join('documents/', filename)


class Document(models.Model):
    file = models.FileField(
        upload_to='documents/',
        storage=FileSystemStorage(location='media')
    )
    original_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.original_name

    def save(self, *args, **kwargs):
        if not self.original_name and self.file:
            # Декодируем имя файла из URL-encoded формата
            self.original_name = urllib.parse.unquote(
                os.path.basename(self.file.name))
        super().save(*args, **kwargs)

    def get_file_url(self):
        return f"/media/documents/{urllib.parse.quote(self.file.name)}"

# TODO: rename to ModuleType


class ExerciseType(models.Model):
    """Тип упражнения (например, "Подставить пропуски", "Разбить по категориям" и т.д.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_name = models.CharField(
        max_length=100,
        help_text="Имя шаблона для рендеринга"
    )

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """Базовое упражнение"""
    title = models.CharField(max_length=25)
    description = models.TextField(blank=True)
    words = models.ManyToManyField('dictionary.Word')
    structure = models.OneToOneField(
        'constructor.ExerciseConstructor',
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.pk})"


class ExerciseConstructor(models.Model):
    """Конструктор упражнений"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)

    def __str__(self):
        return f'[{self.pk}] {self.name}'
