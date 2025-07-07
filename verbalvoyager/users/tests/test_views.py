import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from users.forms import RegistrationUserForm, AuthUserForm
# Import the default PasswordResetForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_auth_register_view_get(client):
    """
    Test that the UserAuthRegisterView renders the correct template and forms.
    """
    url = reverse('auth')  # Updated to use the correct URL pattern name
    response = client.get(url)

    assert response.status_code == 200
    assert 'auth_form' in response.context
    assert 'sign_in_form' in response.context
    assert isinstance(response.context['auth_form'], AuthUserForm)
    assert isinstance(response.context['sign_in_form'], RegistrationUserForm)


@pytest.mark.django_db
def test_user_auth_register_view_post_register(client):
    """
    Test that the UserAuthRegisterView handles registration correctly.
    """
    url = reverse('auth')  # Updated to use the correct URL pattern name
    data = {
        'action': 'register',
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'captcha': 'PASSED'
    }

    response = client.post(url, data)

    if response.context and 'form' in response.context:
        form = response.context['form']
        if form.errors:
            print("Form errors:", form.errors)

    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_user_auth_register_view_post_login(client):
    """
    Test that the UserAuthRegisterView handles login correctly.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123')
    url = reverse('auth')
    data = {
        'action': 'login',
        'username': 'testuser',
        'password': 'testpassword123',
        'captcha': 'PASSED'
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_logout_view(client):
    """
    Test that the UserLogoutView logs out the user and redirects.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123')
    client.login(username='testuser', password='testpassword123')
    url = reverse('logout')

    response = client.get(url)

    assert response.status_code == 302  # Redirect after logout
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_account_view_get(client):
    """
    Test that the UserAccountView renders the correct template and context.
    """
    user = User.objects.create_user(
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
    """
    Test that the CustomPasswordResetView renders the correct template.
    """
    url = reverse('reset_password')
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], PasswordResetForm)
