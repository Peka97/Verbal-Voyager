import pytest
from django.contrib.auth import get_user_model
from users.forms import RegistrationUserForm, AuthUserForm

User = get_user_model()


@pytest.mark.django_db
def test_registration_user_form_valid():
    data = {
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'captcha': 'PASSED'
    }
    form = RegistrationUserForm(data)
    assert form.is_valid()


@pytest.mark.django_db
def test_registration_user_form_invalid():
    data = {
        'username': 'testuser',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'email': 'testuser@example.com',
        'first_name': '',  # Missing required field
        'last_name': 'User',
        'captcha': 'PASSED'
    }
    form = RegistrationUserForm(data)
    assert not form.is_valid()
    assert 'first_name' in form.errors


@pytest.mark.django_db
def test_auth_user_form_valid():
    user = User.objects.create_user(
        username='testuser', password='testpassword123')

    assert User.objects.filter(username='testuser').exists()

    data = {
        'username': 'testuser',
        'password': 'testpassword123',
    }
    form = AuthUserForm(data=data)

    assert form.is_valid(), form.errors
    assert form.get_user() == user


@pytest.mark.django_db
def test_auth_user_form_invalid():
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    form = AuthUserForm(data)
    assert not form.is_valid()
