from django import forms
from django.core.exceptions import ValidationError

from .models import Translation


class TranslationAdminForm(forms.ModelForm):
    class Meta:
        model = Translation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        source_word = cleaned_data.get('source_word')
        target_word = cleaned_data.get('target_word')

        if source_word and target_word:
            if source_word.language == target_word.language:
                raise ValidationError(
                    'Слово-источник и слово-цель должны быть на разных языках.')
            if source_word == target_word:
                raise ValidationError(
                    'Слово-источник и слово-цель должны быть разными.')

        return cleaned_data
