# Generated by Django 4.2.4 on 2024-03-29 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, verbose_name='Название упражнения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exer_student', to=settings.AUTH_USER_MODEL, verbose_name='Ученик')),
                ('teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exer_teacher', to=settings.AUTH_USER_MODEL, verbose_name='Учитель')),
            ],
            options={
                'verbose_name': 'Упражнение',
                'verbose_name_plural': 'Упражнения',
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=50)),
                ('translate', models.CharField(max_length=255)),
                ('lang', models.CharField(choices=[('eng', 'English'), ('fr', 'French'), ('sp', 'Spanish')], default='eng', max_length=10)),
                ('sentences', models.TextField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Слово для изучения',
                'verbose_name_plural': 'Слова для изучения',
            },
        ),
        migrations.CreateModel(
            name='ExerciseResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.CharField(choices=[('1', 'Step 1'), ('2', 'Step 2'), ('3', 'Step 3'), ('4', 'Step 4')], max_length=25)),
                ('result', models.SmallIntegerField()),
                ('exercise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exercise_result', to='exercises.exercise')),
            ],
            options={
                'verbose_name': 'Результат упражнения',
                'verbose_name_plural': 'Результаты упражнений',
            },
        ),
        migrations.AddField(
            model_name='exercise',
            name='words',
            field=models.ManyToManyField(to='exercises.word', verbose_name='Слова'),
        ),
    ]