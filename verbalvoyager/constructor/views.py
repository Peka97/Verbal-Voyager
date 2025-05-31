import json
import logging

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.core.files.storage import default_storage
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, get_object_or_404

from .models import ModuleType, LessonPage, LessonPageConstructor, Document
from dictionary.models import Word


logger = logging.getLogger('django')


class ExerciseConstructorCreateView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'words': Word.objects.filter(language__name='English').all(),
            'exercise_types': ModuleType.objects.all(),
        }
        return render(request, 'constructor/create.html', context)

    def post(self, request, *args, **kwargs):
        try:
            # Парсим данные
            try:
                data = json.loads(request.POST.get('data', '{}'))
                print(data)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON data'
                }, status=400)

            # Валидация
            if not data.get('word_ids'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'No words selected'
                }, status=400)

            # Обработка файлов
            structure = self._process_files(request, data.get('structure', []))

            # Создаем конструктор
            constructor = LessonPageConstructor.objects.create(
                name=data.get(
                    'name', f"Lesson"),
                config={'structure': structure}
            )

            # Создаем страницу урока
            lesson_page = LessonPage.objects.create(
                title=data.get('title', 'New Lesson Page'),
                description=data.get('description', ''),
                structure=constructor
            )
            lesson_page.words.set(Word.objects.filter(pk__in=data['word_ids']))

            return JsonResponse({
                'status': 'success',
                'lesson_page_id': lesson_page.id,
                'redirect_url': reverse('lesson_page', kwargs={'lesson_page_id': lesson_page.id})
            })

        except Exception as e:
            logger.error(f"Error creating exercise: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def _process_files(self, request, structure):
        """Обрабатывает загруженные файлы для документов"""
        for i, item in enumerate(structure):
            if item.get('type_name') == 'document':
                file_key = f'document_{i}'
                if file_key in request.FILES:
                    uploaded_file = request.FILES[file_key]

                    # Создаем или находим документ
                    doc, created = Document.objects.get_or_create(
                        original_name=uploaded_file.name,
                        defaults={
                            'file': uploaded_file,
                            'display_name': item.get('document_name', '')
                        }
                    )

                    # Обновляем структуру
                    item.update({
                        'file_path': doc.get_file_url(),
                        'document_id': doc.id,
                        'document_name': doc.display_name or doc.original_name
                    })
        return structure


class WordAutocompleteView(View):
    def get(self, request):
        search_term = request.GET.get('term', '')

        words = Word.objects.filter(word__icontains=search_term)[:30]
        results = [{
            'id': word.word,
            'text': word.word,
            'translation': word.translations.first().target_word if word.translations.exists() else ''
        } for word in words]

        return JsonResponse({
            'results': results,
            'total_count': Word.objects.count()
        })


class LessonPageView(DetailView):
    model = LessonPage
    template_name = 'constructor/lesson_page.html'
    context_object_name = 'lesson_page'
    pk_url_kwarg = 'lesson_page_id'

    def get_object(self, queryset=None):
        return get_object_or_404(LessonPage, pk=self.kwargs['lesson_page_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['rendered_content'] = self.object.structure.render_structure(
                extra_context={
                    'words': self.object.words.all(),
                    'request': self.request  # Если нужно в шаблонах
                }
            )
        except Exception as e:
            context[
                'rendered_content'] = f"<div class='error'>Ошибка загрузки урока: {str(e)}</div>"

        return context
