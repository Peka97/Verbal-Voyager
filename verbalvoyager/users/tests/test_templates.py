import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from conftest import check_all_static_files_in_templates

from users.views import (
    UserAuthRegisterView,
    UserLogoutView,
    UserAccountView,
    CustomPasswordResetView,
    CustomPasswordResetCompleteView,
    SetUserTimezoneView
)

User = get_user_model()


@pytest.mark.django_db
def test_auth_template(client):
    url = reverse('auth')
    response = client.get(url)
    assert response.status_code == 200
    assert UserAuthRegisterView.template_name in [
        t.name for t in response.templates]


@pytest.mark.django_db
def test_account_template(client):
    user = User.objects.create_user(
        username='testuser', password='testpassword123')
    client.login(username='testuser', password='testpassword123')
    url = reverse('account')
    response = client.get(url)
    assert response.status_code == 200
    assert UserAccountView.template_name in [
        t.name for t in response.templates]


@pytest.mark.django_db
def test_password_reset_complete_template(client):
    url = reverse('password_reset_complete')
    response = client.get(url)
    assert response.status_code == 200
    assert CustomPasswordResetCompleteView.template_name in [
        t.name for t in response.templates]


@pytest.mark.django_db
def test_check_all_static_files_in_templates():
    assert check_all_static_files_in_templates('users') == {}
