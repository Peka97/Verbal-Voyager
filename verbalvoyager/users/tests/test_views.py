import pytest
from django.urls import reverse
from django.contrib.auth.models import Group

# Fixtures


@pytest.fixture
def student_group():
    student_group, _ = Group.objects.get_or_create(name='Student')
    return student_group


@pytest.fixture
def teacher_group():
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    return teacher_group


@pytest.fixture
def groupless_user(django_user_model, student_group):
    groupless_user = django_user_model.objects.create(
        username='groupless_user',
        email='groupless_user@mail.com',
        password='password'
    )
    groupless_user.groups.add(student_group)
    return groupless_user


@pytest.fixture
def student_user(django_user_model):
    student_user = django_user_model.objects.create(
        username='student_user',
        email='student_user@mail.com',
        password='password'
    )
    return student_user


@pytest.fixture
def teacher_user(django_user_model, teacher_group):
    teacher_user = django_user_model.objects.create(
        username='teacher_user',
        email='teacher_user@mail.com',
        password='password'
    )
    teacher_user.groups.add(teacher_group)
    return teacher_user

# Tests

# TODO: не работает авторизация через url тест
# @pytest.mark.django_db
# def test_user_auth_success(client, student_user):
#     url = reverse("auth")
#     data = {
#         'login': student_user.username,
#         'password': student_user.username
#     }
#     response = client.post(url, data, follow=True)
#     assert response.status_code == 200
#     assert '<title> Главная </title>' in response.content.decode()

# TODO: не работает авторизация через url тест
# @pytest.mark.django_db
# def test_user_auth_success_with_redirect_home_page(client, student_user):
#     url = reverse("auth")
#     main_page_url = reverse("")
#     data = {
#         'login': student_user.username,
#         'password': student_user.password
#     }
#     response = client.post(url, data, follow=False)
#     assert response.status_code == 302
#     assert "Неправильное имя пользователя или пароль" not in response.content.decode()


@pytest.mark.django_db
def test_user_logout_with_redirect_home_page(client):
    url = reverse('logout')

    response = client.get(url, follow=False)
    assert response.status_code == 302

    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert '<title> Главная </title>' in response.content.decode()


@pytest.mark.django_db
def test_user_sign_up_get_success(client):
    url = reverse('sign_up')

    response = client.get(url)
    assert response.status_code == 200


# TODO: не работает регистрация через url тест
# @pytest.mark.django_db
# def test_user_sign_up_post_success(client, django_user_model):
    # url = reverse('sign_up')
    # data = {
    #     'first_name': 'first_name',
    #     'last_name': 'last_name',
    #     'email': 'test_username@email.com',
    #     'username': 'test_username',
    #     'password1': 'password123',
    #     'password2': 'password123'
    # }

    # response = client.post(url, data)
    # assert response.status_code == 200
    # assert django_user_model.objects.filter(
    #     username=data['username'],
    #     email=data['email'],
    #     first_name=data['first_name'],
    #     last_name=data['last_name']
    # ).exists() is True

@pytest.mark.django_db
def test_user_reset_password_get_success(client):
    url = reverse('reset_password')

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_activities_groupless_user_account_success(client, groupless_user):
    client.force_login(groupless_user)
    url = reverse("account", kwargs={"current_pane": "activities"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_activities_student_account_success(client, student_user):
    client.force_login(student_user)
    url = reverse("account", kwargs={"current_pane": "activities"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_activities_teacher_account_success(client, teacher_user):
    client.force_login(teacher_user)
    url = reverse("account", kwargs={"current_pane": "activities"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_activities_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "activities"})
    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_account_profile_groupless_user_account_success(client, groupless_user):
    client.force_login(groupless_user)
    url = reverse("account", kwargs={"current_pane": "profile"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_profile_student_account_success(client, student_user):
    client.force_login(student_user)
    url = reverse("account", kwargs={"current_pane": "profile"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_profile_teacher_account_success(client, teacher_user):
    client.force_login(teacher_user)
    url = reverse("account", kwargs={"current_pane": "profile"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_profile_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "profile"})
    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_account_exercises_groupless_user_account_success(client, groupless_user):
    client.force_login(groupless_user)
    url = reverse("account", kwargs={"current_pane": "exercises"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_exercises_student_account_success(client, student_user):
    client.force_login(student_user)
    url = reverse("account", kwargs={"current_pane": "exercises"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_exercises_teacher_account_success(client, teacher_user):
    client.force_login(teacher_user)
    url = reverse("account", kwargs={"current_pane": "exercises"})
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_account_exercises_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "exercises"})
    assert client.get(url).status_code == 302
