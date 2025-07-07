import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from django.test import Client
from users.models import User


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
    client.login(username=teacher_user.username,
                 password=teacher_user.password)
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


@pytest.mark.django_db
def test_teacher_user_save(teacher_user):
    client = Client()
    client.login(
        username='teacher',
        password='teacherpassword',
    )
    url = reverse('admin:users_user_add')

    response = client.get(url)
    assert response.status_code == 200

    data = {
        'username': 'newstudent',
        'password1': 'newpassword123',
        'password2': 'newpassword123',
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert User.objects.filter(username='newstudent').exists()


@pytest.mark.django_db
def test_student_user_not_save(student_user):
    client = Client()
    client.login(username='student', password='studentpassword')
    url = reverse('admin:users_user_add')

    response = client.get(url)
    assert response.status_code == 302

    data = {
        'username': 'newstudent2',
        'password1': 'newpassword123',
        'password2': 'newpassword123',
        'email': 'newstudent2@example.com',
        'first_name': 'New',
        'last_name': 'Student2',
        'timezone': 'Europe/Saratov',
        'groups': [Group.objects.get_or_create(name='Student')[0].id],
    }

    response = client.post(url, data)

    assert response.status_code == 302  # Redirect after successful save
    assert not User.objects.filter(username='newstudent2').exists()
