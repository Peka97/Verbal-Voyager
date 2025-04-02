import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_home_page_get_success(client):
    url = reverse('')

    response = client.get(url)
    assert response.status_code == 200


def test_english_course_page_get_success(client):
    url = reverse('english')

    response = client.get(url)
    assert response.status_code == 200


def test_french_course_page_get_success(client):
    url = reverse('french')

    response = client.get(url)
    assert response.status_code == 200


def test_spanish_course_page_get_success(client):
    url = reverse('spanish')

    response = client.get(url)
    assert response.status_code == 200


def test_portfolio_page_get_success(client):
    url = reverse('portfolio')

    response = client.get(url)
    assert response.status_code == 200


def test_about_project_page_get_success(client):
    url = reverse('about')

    response = client.get(url)
    assert response.status_code == 200


def test_contacts_page_get_success(client):
    url = reverse('contacts')

    response = client.get(url)
    assert response.status_code == 200


def test_faq_page_get_success(client):
    url = reverse('faq')

    response = client.get(url)
    assert response.status_code == 200


def test_err_403_page_get_success(client):
    url = reverse('err_403')

    response = client.get(url)
    assert response.status_code == 403
    assert response.context['title'] == 'Ошибка доступа: 403'


def test_err_404_page_get_success(client):
    url = reverse('err_404')

    response = client.get(url)
    assert response.status_code == 404
    assert response.context['title'] == 'Страница не найдена: 404'


def test_err_500_page_get_success(client):
    url = reverse('err_500')

    response = client.get(url)
    assert response.status_code == 500
    assert response.context['title'] == 'Ошибка сервера: 500'
