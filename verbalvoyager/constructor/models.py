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
            self.original_name = urllib.parse.unquote(
                os.path.basename(self.file.name))
        super().save(*args, **kwargs)

    def get_file_url(self):
        return f"/media/documents/{urllib.parse.quote(self.file.name)}"


class ModuleType(models.Model):
    """Тип упражнения (например, "Подставить пропуски", "Разбить по категориям" и т.д.)"""
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    template_name = models.CharField(
        max_length=20,
        help_text="Имя шаблона для рендеринга"
    )

    def __str__(self):
        return self.name


class LessonPage(models.Model):
    """Базовое упражнение"""
    title = models.CharField(max_length=25)
    description = models.TextField(blank=True)
    words = models.ManyToManyField('dictionary.Word')
    structure = models.OneToOneField(
        'constructor.LessonPageConstructor',
        on_delete=models.CASCADE,
        related_name='lesson_pages'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.pk})"


class LessonPageConstructor(models.Model):
    """Конструктор упражнений"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)

    def __str__(self):
        return f'[{self.pk}] {self.name}'

    def update_structure(self, new_structure):
        """Обновляет структуру с валидацией"""
        if not isinstance(new_structure, list):
            raise ValueError("Structure must be a list")

        self.config['structure'] = new_structure
        self.save()

    def render_structure(self, extra_context=None):
        """Рендеринг структуры с дополнительным контекстом"""
        from django.template.loader import render_to_string

        def render_module(module_data, render_children_only=False):
            try:
                module_type = ModuleType.objects.get(
                    code=module_data['type_name'])

                # Если нужно рендерить только детей (для вложенных модулей)
                if render_children_only:
                    children_html = []
                    for child in module_data.get('children', []):
                        children_html.append(render_module(child))
                    return "".join(children_html)

                context = {
                    'module': module_data,
                    'children': []
                }

                # Добавляем дополнительный контекст
                if extra_context:
                    context.update(extra_context)

                # Рендерим вложенные модули (только их содержимое, без оберток)
                for child in module_data.get('children', []):
                    context['children'].append(render_module(
                        child, render_children_only=True))

                return render_to_string(
                    f"constructor/includes/exercise_types/{module_type.template_name}",
                    context
                )
            except ModuleType.DoesNotExist:
                return ""

        return "".join(render_module(module) for module in self.config.get('structure', []))
