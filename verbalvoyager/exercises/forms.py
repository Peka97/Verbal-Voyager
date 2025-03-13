import logging

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from logger import get_logger
from dictionary.models import EnglishWord, FrenchWord, IrregularEnglishVerb


logger = get_logger()
User = get_user_model()


class ExerciseForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}),
        label=False
    )
    student = forms.ModelChoiceField(
        queryset=User.objects.exclude(username__startswith='_') &
        User.objects.exclude(username__startswith='test_') &
        User.objects.exclude(groups__name='Teacher'),
        to_field_name=None,
        label='Студент'
    )
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Teacher'),
        label='Учитель'
    )


class ExerciseDialogAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        text = self.cleaned_data.get("text")
        if not text:
            raise ValidationError('Поле "Текст" не заполнено.')

        for line in text.split('\n'):
            if line == '\r':
                continue

            if 'Scene:' not in line and ':' not in line:
                logger.error(f'Invalid line: {line}')
                raise ValidationError(
                    f'Не выполнены требования к полю "Текст". Они прописаны под полем. [ Реплика с ошибкой: {line} ]')

        words = self.cleaned_data["words"]

        for word in words:
            if word.word.lower() not in text.lower():
                raise ValidationError(f'Word "{word.word}" not in text.')

        return cleaned_data


class ExerciseIrregularEnglishVerbAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
