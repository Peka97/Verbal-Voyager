import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

logger = logging.getLogger('django')
User = get_user_model()


@receiver([post_save, post_delete], sender=Group)
def invalidate_groups_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern("global_*_users_in_group_*")
    except Exception as err:
        logger.error(err, exc_info=True)


@receiver([post_save, post_delete], sender=User)
def invalidate_users_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern("global_*_users_in_group_*")
    except Exception as err:
        logger.error(err, exc_info=True)
