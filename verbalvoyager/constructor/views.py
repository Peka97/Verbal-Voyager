import json

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.shortcuts import redirect, render

from .models import ExerciseConstructor
from dictionary.models import Word
from .models import ExerciseType, Exercise, Document


import json
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import redirect
from django.urls import reverse


class ExerciseConstructorCreateView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'words': Word.objects.filter(language__name='English').all(),
            'exercise_types': ExerciseType.objects.all()
        }
        return render(request, 'constructor/create.html', context)

    def post(self, request, *args, **kwargs):
        # Обработка FormData (когда есть файлы)
        # if request.FILES:
        #     try:
        #         data = json.loads(request.POST.get('data'))
        #         files = request.FILES
        #     except (json.JSONDecodeError, AttributeError) as e:
        #         return JsonResponse({'error': 'Invalid data format'}, status=400)
        # else:
        #     # Обработка JSON
        #     try:
        #         data = json.loads(request.body)
        #     except json.JSONDecodeError:
        #         return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # words = data.get('word_ids', [])
        # structure = data.get('structure', [])

        # # Создаем конструктор
        # constructor = ExerciseConstructor.objects.create(
        #     config={
        #         'structure': structure
        #     }
        # )

        # # Создаем упражнение
        # exercise = Exercise.objects.create(
        #     title='ExerciseName',
        #     description='ExerciseName',
        #     structure=constructor
        # )

        # # Добавляем слова
        # if words:
        #     words_qs = Word.objects.filter(pk__in=words)
        #     exercise.words.set(words_qs)

        # # Обработка файлов (если есть)
        # if request.FILES:
        #     for i, item in enumerate(structure):
        #         if item.get('type_name') == 'document':
        #             file_key = f'document_{i}'
        #             if file_key in files:
        #                 uploaded_file = files[file_key]
        #                 document = Document.objects.create(
        #                     file=uploaded_file,
        #                     original_name=uploaded_file.name
        #                 )

        #                 # Сохраняем только относительный путь к файлу
        #                 file_path = f"documents/{uploaded_file.name}"
        #                 item['file_path'] = file_path

        #     constructor.config['structure'] = structure
        #     constructor.save()

        # return JsonResponse({
        #     'status': 'success',
        #     'exercise_id': exercise.id,
        #     'redirect_url': reverse('exercise', kwargs={'exercise_id': exercise.id})
        # })
        try:
            # Определяем тип запроса (JSON или FormData)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = json.loads(request.POST.get('data', '{}'))

            print(data)

            words = data.get('word_ids', [])
            structure = data.get('structure', [])

            # Обработка файлов
            if request.FILES:
                for i, item in enumerate(structure):
                    if item.get('type_name') == 'document':
                        file_key = f'document_{i}'
                        if file_key in request.FILES:
                            uploaded_file = request.FILES[file_key]

                            file_name = item.get('document_name') if item.get(
                                'document_name') else uploaded_file.name

                            # Проверяем, не загружен ли файл ранее
                            existing_doc = Document.objects.filter(
                                original_name=file_name
                            ).first()

                            if existing_doc and default_storage.exists(existing_doc.file.name):
                                # Используем существующий файл
                                item['file_path'] = existing_doc.get_file_url()
                                item['document_id'] = existing_doc.id
                            else:
                                # Создаем новую запись
                                doc = Document.objects.create(
                                    file=uploaded_file,
                                    original_name=file_name
                                )
                                item['file_path'] = doc.get_file_url()
                                item['document_id'] = doc.id

            # Создание объектов
            constructor = ExerciseConstructor.objects.create(
                config={'structure': structure}
            )

            exercise = Exercise.objects.create(
                title='New Exercise',
                description='Auto-generated exercise',
                structure=constructor
            )

            if words:
                exercise.words.set(Word.objects.filter(pk__in=words))

            return JsonResponse({
                'status': 'success',
                'exercise_id': exercise.id,
                'redirect_url': reverse('exercise', kwargs={'exercise_id': exercise.id})
            })

        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


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


class ExerciseView(TemplateView):
    template_name = 'constructor/exercise.html'

    def get_context_data(self, exercise_id, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = Exercise.objects.get(pk=exercise_id)
        context['exercise'] = exercise

        context['structure'] = [
            ExerciseType.objects.get(pk=int(ex_type['type_id']))
            for ex_type in exercise.structure.config['structure']
        ]
        print(context['exercise'])
        return context

    def get(self, request, exercise_id, *args, **kwargs):
        context = self.get_context_data(exercise_id)
        return self.render_to_response(context)
