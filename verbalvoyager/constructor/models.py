import os
import urllib.parse

from django.core.files.storage import FileSystemStorage
from django.db import models


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
    code = models.CharField(max_length=25, blank=True)
    description = models.TextField(blank=True)
    template_name = models.CharField(
        max_length=50,
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
        from django.core.exceptions import ObjectDoesNotExist
        from django.template.loader import render_to_string

        section_counter = 1

        if not hasattr(self, 'config') or not isinstance(self.config, dict):
            return "<div class='error'>Invalid lesson configuration</div>"

        def render_module(module_data, depth=0):
            nonlocal section_counter
            try:
                if not isinstance(module_data, dict):
                    return ""

                module_type = ModuleType.objects.get(
                    code=module_data.get('type_name'))

                context = {
                    'module': module_data,
                    'depth': depth,
                    'words': extra_context.get('words', []) if extra_context else [],
                }

                # Для секций сначала рендерим детей, затем передаем их в контекст
                if module_type.code == 'section':
                    context['section_id'] = f'section_{section_counter}'
                    section_counter += 1

                    children_html = []
                    for child in module_data.get('children', []):
                        child_html = render_module(child, depth + 1)
                        if child_html:
                            children_html.append(child_html)
                    context['children'] = children_html
                # Для других типов модулей просто рендерим их как есть
                else:
                    # Если у не-секционного модуля есть дети (что маловероятно), рендерим их внутри
                    children_html = []
                    for child in module_data.get('children', []):
                        child_html = render_module(child, depth + 1)
                        if child_html:
                            children_html.append(child_html)
                    context['children'] = children_html

                template_path = f"constructor/includes/exercise_types/{module_type.template_name}"
                return render_to_string(template_path, context)

            except ObjectDoesNotExist:
                return f"<div class='error'>Module type {module_data.get('type_name')} not found. Module data: {module_data}</div>"
            except Exception as e:
                return f"<div class='error'>Error rendering module: {str(e)}</div>"

        structure = self.config.get('structure', [])
        if not structure:
            return "<div class='info'>Упражнение не содержит модулей</div>"

        return "".join(render_module(module) for module in structure if module)
