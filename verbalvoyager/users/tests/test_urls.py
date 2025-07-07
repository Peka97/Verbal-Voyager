from django.urls import reverse, resolve
from users.views import UserAuthRegisterView, UserLogoutView, UserAccountView, CustomPasswordResetView


def test_auth_url():
    url = reverse('auth')
    assert resolve(url).func.view_class == UserAuthRegisterView


def test_logout_url():
    url = reverse('logout')
    assert resolve(url).func.view_class == UserLogoutView


def test_account_url():
    url = reverse('account')
    assert resolve(url).func.view_class == UserAccountView


def test_reset_password_url():
    url = reverse('reset_password')
    assert resolve(url).func.view_class == CustomPasswordResetView
