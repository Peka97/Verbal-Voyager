from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse
import pytest

from users.models import User


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')


@pytest.fixture
def teacher_user():
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    user = User.objects.create_user(
        username='teacher', password='teacherpassword', email='teacher@example.com')
    user.groups.add(teacher_group)
    return user


@pytest.fixture
def student_user():
    student_group, _ = Group.objects.get_or_create(name='Student')
    user = User.objects.create_user(
        username='student', password='studentpassword', email='student@example.com')
    user.groups.add(student_group)
    return user


@pytest.mark.django_db
def test_admin_user_list(admin_user):
    client = Client()
    client.login(username='admin', password='adminpassword')
    url = reverse('admin:users_user_changelist')

    response = client.get(url)

    assert response.status_code == 200
    assert 'username' in response.context['cl'].list_display
    assert 'last_name' in response.context['cl'].list_display
    assert 'first_name' in response.context['cl'].list_display
    assert 'get_groups' in response.context['cl'].list_display
    assert 'email' in response.context['cl'].list_display


@pytest.mark.django_db
def test_teacher_user_list(teacher_user):
    client = Client()
    client.login(username='teacher', password='teacherpassword')
    url = reverse('admin:users_user_changelist')

    response = client.get(url)

    assert response.status_code == 302  # Redirect to login page


@pytest.mark.django_db
def test_student_user_list(student_user):
    client = Client()
    client.login(username='student', password='studentpassword')
    url = reverse('admin:users_user_changelist')

    response = client.get(url)

    assert response.status_code == 302  # Redirect to login page


@pytest.mark.django_db
def test_admin_user_save(admin_user):
    client = Client()
    client.login(username='admin', password='adminpassword')
    url = reverse('admin:users_user_add')

    data = {
        'username': 'newuser',
        'password1': 'newpassword123',
        'password2': 'newpassword123',
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'timezone': 'Europe/Saratov',
        'groups': [Group.objects.get_or_create(name='Student')[0].id],
    }

    response = client.post(url, data)

    assert response.status_code == 302  # Redirect after successful save
    assert User.objects.filter(username='newuser').exists()


# @pytest.mark.django_db
# def test_teacher_user_save(teacher_user):
#     client = Client()
#     # Ensure the teacher is logged in
#     client.login(username='teacher', password='teacherpassword')
#     url = reverse('admin:users_user_add')

#     data = {
#         'username': 'newstudent',
#         'password1': 'newpassword123',
#         'password2': 'newpassword123',
#         'email': 'newstudent@example.com',
#         'first_name': 'New',
#         'last_name': 'Student',
#         'timezone': 'Europe/Saratov',
#         'groups': [Group.objects.get_or_create(name='Student')[0].id],
#     }

#     response = client.post(url, data)

#     assert response.status_code == 302  # Redirect after successful save
#     assert User.objects.filter(username='newstudent').exists()
