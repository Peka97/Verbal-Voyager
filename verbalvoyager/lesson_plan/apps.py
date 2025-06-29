from django.apps import AppConfig


class LessonPlanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lesson_plan'
    verbose_name = 'Приложение "План урока"'

    def ready(self):
        import lesson_plan.signals  # noqa
