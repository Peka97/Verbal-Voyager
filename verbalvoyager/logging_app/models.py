from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ActionLog(models.Model):
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name='Временная метка')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Тип содержимого'
    )
    object_id = models.PositiveIntegerField(verbose_name='ID объекта')
    content_object = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=255, verbose_name='Действие')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        user_repr = str(self.user) if self.user else "Аноним"
        content_repr = self.get_content_object_safe()
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {user_repr} - {self.action} - {content_repr}"

    def get_content_object_safe(self):
        """Безопасное получение связанного объекта"""
        try:
            return self.content_object
        except AttributeError:
            return "Удалённый объект"

    class Meta:
        verbose_name = 'Лог действий'
        verbose_name_plural = 'Логи действий'
        ordering = ['-timestamp']
