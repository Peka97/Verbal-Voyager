import logging

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import ExerciseWords


logger = logging.getLogger('django')
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
                raise ValidationError(
                    f'Не выполнены требования к полю "Текст". Они прописаны под полем. [ Реплика с ошибкой: {line} ]')

        words = self.cleaned_data["words"]

        for word in words:
            if word.word.lower() not in text.lower() and word.translation.lower() not in text.lower():
                raise ValidationError(f'Word "{word.word}" not in text.')

        return cleaned_data


class ExerciseIrregularEnglishVerbAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data


class NewWordsExerciseForm(forms.ModelForm):
    class Meta:
        model = ExerciseWords
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        lang = cleaned_data.get('lang')
        translations = cleaned_data.get('words')

        if not lang:
            raise ValidationError('Поле "Язык" не заполнено.')

        for translation in translations.all():
            print(lang.name)
            print(translation.source_word.language.name)
            if lang.name == 'Russian' and translation.source_word.language.name == 'English':
                continue
            elif translation.source_word.language != lang:
                raise ValidationError(
                    f'Слово "{translation}" не подходит для языка "{lang.name}"')

        return cleaned_data


class NewExerciseDialogAdminForm(forms.ModelForm):
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

        translations = self.cleaned_data["words"]

        for translation in translations:
            if translation.source_word.word.lower() not in text.lower() and translation.target_word.word.lower() not in text.lower():
                raise ValidationError(
                    f'Word "{translation.source_word.word}" not in text.')

        return cleaned_data
