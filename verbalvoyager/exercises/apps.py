from django.apps import AppConfig


class ExercisesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exercises'
    verbose_name = 'Приложение "Упражнения"'

    def ready(self):
        import exercises.signals  # noqa
