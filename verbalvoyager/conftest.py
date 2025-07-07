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
    for path in settings.TEMPLATES[0]['DIRS']:
        print(path)
    template_dirs = \
        [
            path for path in settings.TEMPLATES[0]['DIRS']
            if f'{app_name}/templates/{app_name}' in path
        ]
    print('Template dirs:', template_dirs, sep='\n')

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
