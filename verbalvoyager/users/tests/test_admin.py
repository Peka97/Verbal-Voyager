from django.test import Client
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_create_user_from_admin_panel(admin_client: Client, django_user_model):
    users_count = django_user_model.objects.count()
    data = {
        'username': 'new_user',
        'password1': 'nZ8Y8gW_zA',
        'password2': 'nZ8Y8gW_zA'
    }

    url = reverse('admin:users_user_add')

    response = admin_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert 'был успешно добавлен.' in response.content.decode(
    )
    assert django_user_model.objects.count() == users_count + 1

    new_user = django_user_model.objects.filter(username=data['username'])
    assert new_user.exists() is True
