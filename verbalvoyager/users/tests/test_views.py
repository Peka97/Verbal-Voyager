from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.test import Client
from django.urls import reverse
import pytest

from users.forms import AuthUserForm, RegistrationUserForm


User = get_user_model()


@pytest.mark.django_db
def test_user_auth_register_view_get(client):
    url = reverse('auth')
    response = client.get(url)

    assert response.status_code == 200
    assert 'auth_form' in response.context
    assert 'sign_in_form' in response.context
    assert isinstance(response.context['auth_form'], AuthUserForm)
    assert isinstance(response.context['sign_in_form'], RegistrationUserForm)


@pytest.mark.django_db
def test_user_auth_register_view_post_register(client):
    url = reverse('auth')
    data = {
        'action': 'register',
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        "captcha": "PASSED",
    }

    response = client.post(url, data)

    if response.context and 'form' in response.context:
        form = response.context['form']
        if form.errors:
            pass

    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_user_auth_register_view_post_login(client):
    User.objects.create_user(
        username='testuser', password='testpassword123')
    url = reverse('auth')
    data = {
        'action': 'login',
        'username': 'testuser',
        'password': 'testpassword123'
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_logout_view(client):
    User.objects.create_user(
        username='testuser', password='testpassword123')
    client.login(username='testuser', password='testpassword123')
    url = reverse('logout')
    response = client.get(url)

    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_account_view_get(client):
    User.objects.create_user(
        username='testuser', password='testpassword123')
    client.login(username='testuser', password='testpassword123')
    url = reverse('account')

    response = client.get(url)

    assert response.status_code == 200
    assert 'user_is_teacher' in response.context
    assert 'user_is_supervisor' in response.context
    assert 'timezone_form' in response.context
    assert 'courses' in response.context
    assert 'current_pane' in response.context


@pytest.mark.django_db
def test_custom_password_reset_view_get(client):
    url = reverse('reset_password')
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], PasswordResetForm)
