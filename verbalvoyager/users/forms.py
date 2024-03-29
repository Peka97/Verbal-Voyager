from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm


User = get_user_model()


class RegistrationUserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}
        ),
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}
        ),
        label='Фамилия'
    )
    email = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}
        ),
        label='Адрес электронной почты'
    )

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email'
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = field


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField()
