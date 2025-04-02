from django.contrib.contenttypes.models import ContentType

from .models import ActionLog


def log_action(user, obj, action, description=''):
    content_type = ContentType.objects.get_for_model(obj)
    ActionLog.objects.create(
        user=user,
        content_type=content_type,
        object_id=obj.pk,
        action=action,
        description=description
    )
