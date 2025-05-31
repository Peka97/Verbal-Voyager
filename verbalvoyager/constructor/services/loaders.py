
from ..models import Document


def process_files(view, request, structure):
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
