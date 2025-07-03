import pytest

from django.contrib.auth.models import Group, Permission

from users.models import User


@pytest.fixture(autouse=True)
def create_groups():
    Group.objects.get_or_create(name='Teacher')
    Group.objects.get_or_create(name='Student')
    Group.objects.get_or_create(name='Supervisor')


@pytest.fixture
def student_user():
    student_group = Group.objects.get(name='Student')
    user = User.objects.create_user(
        username='student', password='studentpassword', email='student@example.com')
    user.groups.add(student_group)
    return user


@pytest.fixture
def teacher_user():
    teacher_group = Group.objects.get(name='Teacher')
    user = User.objects.create_user(
        username='teacher', password='teacherpassword', email='teacher@example.com')
    user.groups.add(teacher_group)
    user.is_staff = True

    # Добавляем разрешения для доступа к админке
    permissions = Permission.objects.filter(
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user'])
    user.user_permissions.add(*permissions)

    return user


@pytest.fixture
def supervisor_user():
    supervisor_group = Group.objects.get(name='Supervisor')
    user = User.objects.create_user(
        username='supervisor', password='supervisorpassword', email='supervisor@example.com')
    user.groups.add(supervisor_group)

    # Добавляем разрешения для доступа к админке
    permissions = Permission.objects.filter(
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user'])
    user.user_permissions.add(*permissions)

    return user


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')
