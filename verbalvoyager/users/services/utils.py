from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import pytz


def get_current_month_range(user):
    """
    Возвращает начало и конец текущего месяца в часовом поясе пользователя
    :param user: объект пользователя Django с полем timezone
    :return: кортеж (начало месяца, конец месяца) в правильном часовом поясе
    """
    # Получаем часовой пояс пользователя
    user_tz = pytz.timezone(
        user.timezone) if user.timezone else timezone.get_current_timezone()

    # Текущее время в часовом поясе пользователя
    now = timezone.now().astimezone(user_tz)

    # Первый день месяца (00:00:00)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Последний день месяца (23:59:59.999999)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - \
        timedelta(microseconds=1)

    # Конвертируем в UTC для хранения в базе данных
    first_day_utc = first_day.astimezone(pytz.UTC)
    last_day_utc = last_day.astimezone(pytz.UTC)

    return first_day_utc, last_day_utc
