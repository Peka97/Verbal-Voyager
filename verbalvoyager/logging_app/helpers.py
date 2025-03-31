from .views import log_action as l_a


def log_action(func):
    def wrapper(self, request, obj, form, change, *args, **kwargs):
        user = request.user

        if obj:
            obj.save()
            action_type = 'created' if not change else 'updated'
            action = f"{self} [{obj.pk}] {action_type}"
            l_a(user, obj, action)

        return func(self, request, obj, form, change, *args, **kwargs)

    return wrapper
