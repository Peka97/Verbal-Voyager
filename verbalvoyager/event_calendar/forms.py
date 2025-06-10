
from django import forms
from django.contrib.auth import get_user_model

from .models import Lesson


User = get_user_model()


class LessonForm(forms.ModelForm):
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


class LessonAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LessonAdminForm, self).__init__(*args, **kwargs)
        self.fields['teacher_id'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        self.fields['student_id'].queryset = User.objects.filter(
            groups__name__in=['Student'])


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

    students = forms.ModelChoiceField(
        queryset=User.objects.exclude(username__startswith='_') &
        User.objects.exclude(username__startswith='test_') &
        User.objects.exclude(groups__name='Teacher'),
        to_field_name=None,
        label='Студенты'
    )
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Teacher'),
        label='Учитель'
    )


class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        self.fields['teacher_id'].queryset = User.objects.filter(
            groups__name__in=['Teacher'])
        self.fields['teacher_id'].initial = User.objects.get(
            username='Elizabeth')
        self.fields['students'].queryset = User.objects.filter(
            groups__name__in=['Student'])
