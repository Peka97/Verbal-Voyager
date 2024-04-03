from typing import Any

from django import forms
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth import get_user_model

from .models import Lesson


User = get_user_model()


class LessonForm(ModelForm):
    title = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}),
        label=False
    )
    description = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            {'class': 'form-control'}),
        label=False
    )
    datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'},
        )
    )
    is_paid = forms.BooleanField(
        initial=True,
        label='Оплачено'
    )
    status = forms.ChoiceField(
        choices=[
            ('P', 'planned'),
            ('M', 'missed'),
            ('D', 'done'),
            ('C', 'canceled')
        ],
        label='Статус'
    )
    students = forms.ModelChoiceField(
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

    class Meta:
        model = Lesson
        fields = "__all__"
        exclude = ("datetime", )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(LessonForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            pass
            # if field == 'is_paid':
            #     continue
            # self.fields[field].widget.attrs['class'] = 'form-control'
            # self.fields[field].widget.attrs['placeholder'] = field


class LessonAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LessonAdminForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        self.fields['students'].queryset = User.objects.filter(
            groups__name__in=['Student'])
