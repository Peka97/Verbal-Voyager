import logging

from django import forms
from django.contrib.auth import get_user_model

from .models import Exercise


logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.FileHandler(
#     '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
# )
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


class ExerciseAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExerciseAdminForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        self.fields['teacher'].initial = User.objects.get(
            username='Elizabeth')
        self.fields['student'].queryset = User.objects.filter(
            groups__name__in=['Student'])