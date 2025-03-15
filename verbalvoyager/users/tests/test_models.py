import pytest


@pytest.mark.django_db
def test_user_create_and_delete(django_user_model):
    users_count_under_create = django_user_model.objects.count()
    django_user_model.objects.create_user('user', 'user@mail.com', 'password')
    assert django_user_model.objects.count() == users_count_under_create + 1

    users_count_under_delete = django_user_model.objects.count()

    django_user_model.objects.filter(username='user').delete()
    assert django_user_model.objects.count() == users_count_under_delete - 1
