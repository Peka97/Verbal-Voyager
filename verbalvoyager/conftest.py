import os
from pathlib import Path
import re


import pytest
from django.apps import apps
from django.contrib.staticfiles import finders
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import SuspiciousFileOperation

from users.models import User


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')


@pytest.fixture
def teacher_user(teacher_group):
    user = User.objects.create_user(
        username='teacher',
        password='teacherpassword',
        email='teacher@example.com',
        is_staff=True
    )
    user.groups.add(teacher_group)
    return user


@pytest.fixture
def student_user():
    student_group, _ = Group.objects.get_or_create(name='Student')
    user = User.objects.create_user(
        username='student',
        password='studentpassword',
        email='student@example.com'
    )
    user.groups.add(student_group)
    return user


@pytest.fixture
def teacher_group():
    group = Group.objects.get_or_create(name='Teacher')[0]
    permissions = Permission.objects.filter(
        codename__in=[
            'view_logentry,'
            'view_group,'
            'view_permission,'
            'view_course,'
            'add_lesson,'
            'change_lesson,'
            'delete_lesson,'
            'view_lesson,'
            'add_lessontask,'
            'change_lessontask,'
            'delete_lessontask,'
            'view_lessontask,'
            'add_project,'
            'change_project,'
            'delete_project,'
            'view_project,'
            'add_projecttask,'
            'change_projecttask,'
            'delete_projecttask,'
            'view_projecttask,'
            'view_projecttype,'
            'add_review,'
            'change_review,'
            'view_review,'
            'view_exercisedialogresult,'
            'view_exercisewordsresult,'
            'view_newexerciseirregularenglishverbresult,'
            'add_exercisecategory,'
            'change_exercisecategory,'
            'delete_exercisecategory,'
            'view_exercisecategory,'
            'add_exercisedialog,'
            'change_exercisedialog,'
            'delete_exercisedialog,'
            'view_exercisedialog,'
            'add_exercisewords,'
            'change_exercisewords,'
            'delete_exercisewords,'
            'view_exercisewords,'
            'add_newexerciseirregularenglishverb,'
            'change_newexerciseirregularenglishverb,'
            'delete_newexerciseirregularenglishverb,'
            'view_newexerciseirregularenglishverb,'
            'add_englishlessonmainaims,'
            'change_englishlessonmainaims,'
            'delete_englishlessonmainaims,'
            'view_englishlessonmainaims,'
            'add_englishlessonplan,'
            'change_englishlessonplan,'
            'delete_englishlessonplan,'
            'view_englishlessonplan,'
            'add_englishlessonsubsidiaryaims,'
            'change_englishlessonsubsidiaryaims,'
            'delete_englishlessonsubsidiaryaims,'
            'view_englishlessonsubsidiaryaims,'
            'add_user,'
            'change_user,'
            'view_user,'
        ]
    )
    group.permissions.add(*permissions)
    return group

# TODO: to delete afted separete for signle fixture


@pytest.fixture(autouse=True)
def create_groups():
    Group.objects.get_or_create(name='Teacher')
    Group.objects.get_or_create(name='Student')
    Group.objects.get_or_create(name='Supervisor')


@pytest.fixture(autouse=True)
def add_permissions_to_teacher_group():
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    permissions = Permission.objects.filter(
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user'])
    teacher_group.permissions.add(*permissions)


@pytest.fixture
def supervisor_user():
    supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
    user = User.objects.create_user(
        username='supervisor', password='supervisorpassword', email='supervisor@example.com')
    user.groups.add(supervisor_group)
    permissions = Permission.objects.filter(
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user'])
    user.user_permissions.add(*permissions)
    return user


def find_all_template_files(app_name):
    """
    Находит все файлы шаблонов (*.html) в указанных директориях.
    Если директории не указаны, использует настройки Django TEMPLATES['DIRS'].
    """
    from django.conf import settings

    template_dirs = \
        [
            path for path in settings.TEMPLATES[0]['DIRS']
            if f'{app_name}/templates/{app_name}' in path
        ]

    template_files = []

    for template_dir in template_dirs:
        for root, _, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    full_path = os.path.join(root, file)
                    template_files.append(full_path)

    for app in apps.get_app_configs():
        app_template_dir = os.path.join(app.path, 'templates')
        if os.path.exists(app_template_dir):
            for root, _, files in os.walk(app_template_dir):
                if f'/{app_name}/templates/{app_name}/' not in root:
                    continue
                for file in files:
                    if file.endswith('.html'):
                        full_path = os.path.join(root, file)
                        template_files.append(full_path)

    return template_files


def extract_static_paths_from_template_content(content):
    """
    Извлекает все пути к статике из содержимого шаблона.
    Возвращает список уникальных путей.
    """
    static_patterns = [
        # {% static 'path/to/file' %}
        r"{%\s*static\s*['\"]([^'\"]+)['\"]\s*%}",
        # {{ static 'path/to/file' }}
        r"{{[\s'\"]*static[\s'\"]*['\"]([^'\"]+)['\"][\s'\"]*}}",
        r"url\(['\"]?([^'\")]+)['\"]?\)",  # url('path/to/file') в CSS/JS
        r"['\"](/static/[^'\"]+)['\"]",  # Прямые ссылки /static/path/to/file
    ]

    static_paths = set()  # Используем set, чтобы избежать дубликатов

    for pattern in static_patterns:
        matches = re.findall(pattern, content)
        static_paths.update(matches)

    return list(static_paths)


def check_all_static_files_in_templates(app_name):
    """
    Проверяет, что все статические файлы, используемые в шаблонах, существуют.
    Возвращает словарь с отсутствующими файлами и в каких шаблонах они используются.
    """
    template_files = find_all_template_files(app_name)
    missing_files = {}

    for template_path in template_files:
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()

        static_paths = extract_static_paths_from_template_content(content)

        for static_path in static_paths:
            try:
                if not finders.find(static_path):
                    if static_path not in missing_files:
                        missing_files[static_path] = []
                    missing_files[static_path].append(template_path)
            except SuspiciousFileOperation:
                continue

    return missing_files


def find_all_js_files(app_name):
    """
    Находит все JS файлы в статике указанного приложения.
    Ищет файлы по пути: app_name/static/app_name/js/
    Возвращает абсолютные пути к файлам.
    """
    from django.conf import settings
    import os
    from django.apps import apps

    js_files = []

    for static_dir in settings.STATICFILES_DIRS:
        static_dir = os.path.normpath(static_dir)
        app_static_path = os.path.join(static_dir, app_name, 'js')
        app_static_path = os.path.normpath(app_static_path)

        if os.path.exists(app_static_path):
            for root, _, files in os.walk(app_static_path):
                for file in files:
                    if file.endswith('.js'):
                        full_path = os.path.join(root, file)
                        js_files.append(full_path)

    for app_config in apps.get_app_configs():
        app_static_path = os.path.join(
            app_config.path, 'static', app_name, 'js')
        app_static_path = os.path.normpath(app_static_path)

        if os.path.exists(app_static_path):
            for root, _, files in os.walk(app_static_path):
                for file in files:
                    if file.endswith('.js') and not file.startswith('_'):
                        full_path = os.path.join(root, file)
                        js_files.append(full_path)

    return js_files


def extract_imports_from_js_content(content):
    """
    Извлекает все пути из импортов в JS файле.
    Возвращает список уникальных путей.
    """
    # Регулярные выражения для разных форматов импортов
    import_patterns = [
        r"from\s+['\"]([^'\"]+)['\"]",  # from 'path'
        # import x from 'path'
        r"import\s+[^'\"\n]+\s+from\s+['\"]([^'\"]+)['\"]",
        r"import\s+['\"]([^'\"]+)['\"]",  # import 'path'
        r"import\(['\"]([^'\"]+)['\"]\)",  # import('path')
    ]

    import_paths = set()

    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        import_paths.update(matches)

    return list(import_paths)


def resolve_import_path(import_path, current_js_path, app_name):
    """
    Преобразует путь импорта в абсолютный путь к файлу.
    Учитывает структуру Django static files.
    """
    # Если это абсолютный путь (/static/...)
    if import_path.startswith('/static/'):
        # Удаляем /static/ и возвращаем относительный путь
        return import_path[len('/static/'):]

    # Если путь начинается с ../ или ./
    if import_path.startswith(('../', './')):
        # Получаем директорию текущего JS файла
        current_dir = os.path.dirname(current_js_path)
        # Нормализуем путь
        absolute_path = os.path.normpath(
            os.path.join(current_dir, import_path))

        # Пытаемся найти путь относительно static/app_name/
        static_prefix = os.path.join('static', app_name)
        if static_prefix in absolute_path:
            # Вырезаем часть до static/app_name/
            parts = absolute_path.split(static_prefix)
            if len(parts) > 1:
                return os.path.join(app_name, parts[1].lstrip('/\\'))

        # Если не нашли, возвращаем полный путь
        return absolute_path

    # Для простых путей (без ../ и ./)
    # Предполагаем, что это относительно /static/app_name/js/
    return os.path.join(app_name, 'js', import_path)


def check_all_js_imports(app_name):
    """
    Проверяет, что все импорты в JS файлах существуют.
    Возвращает словарь с отсутствующими файлами.
    """
    js_files = find_all_js_files(app_name)
    missing_imports = {}

    for js_path in js_files:
        with open(js_path, 'r', encoding='utf-8') as file:
            content = file.read()

        import_paths = extract_imports_from_js_content(content)

        for import_path in import_paths:
            resolved_path = resolve_import_path(import_path, js_path, app_name)

            # Проверяем существование файла через систему статики Django
            if not finders.find(resolved_path):
                if resolved_path not in missing_imports:
                    missing_imports[resolved_path] = []
                missing_imports[resolved_path].append(js_path)
    return missing_imports


def check_all_static_references(app_name):
    """
    Проверяет все ссылки на статику в шаблонах и импорты в JS файлах.
    Возвращает объединенный словарь с отсутствующими файлами.
    """
    missing_templates = check_all_static_files_in_templates(app_name)
    missing_js = check_all_js_imports(app_name)

    # Объединяем результаты
    all_missing = {}
    all_missing.update(missing_templates)

    for path, files in missing_js.items():
        if path in all_missing:
            all_missing[path].extend(files)
        else:
            all_missing[path] = files

    return all_missing
