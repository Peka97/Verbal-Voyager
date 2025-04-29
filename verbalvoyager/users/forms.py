from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


User = get_user_model()


class AuthUserForm(AuthenticationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'password1',
        ]


class RegistrationUserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=50,
        label='Фамилия'
    )
    email = forms.CharField(
        max_length=50,
        label='Адрес электронной почты'
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'id': 'registerCaptcha',
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email',
            'captcha'
        ]

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super(UserCreationForm, self).__init__(*args, **kwargs)

            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'input'})

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField()


class TimezoneForm(forms.ModelForm):
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'id': 'timezoneCaptcha',
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['timezone', 'captcha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timezone'].widget.attrs.update(
            {'class': 'form-select', 'aria-label': 'Выберите часовой пояс'})
        self.fields['timezone'].help_text = "Выберите ваш часовой пояс, чтобы время отображалось корректно."
