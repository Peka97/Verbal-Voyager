from django.urls import reverse, resolve
import pytest
from users.views import UserAuthRegisterView, UserLogoutView, UserAccountView, CustomPasswordResetView


@pytest.mark.django_db
def test_auth_url():
    url = reverse('auth')
    assert resolve(url).func.view_class == UserAuthRegisterView


@pytest.mark.django_db
def test_logout_url():
    url = reverse('logout')
    assert resolve(url).func.view_class == UserLogoutView


@pytest.mark.django_db
def test_account_url():
    url = reverse('account')
    assert resolve(url).func.view_class == UserAccountView


@pytest.mark.django_db
def test_reset_password_url():
    url = reverse('reset_password')
    assert resolve(url).func.view_class == CustomPasswordResetView
