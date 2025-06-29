from django.apps import AppConfig


class EventCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event_calendar'
    verbose_name = 'Приложение "События"'

    def ready(self):
        import event_calendar.signals  # noqa
