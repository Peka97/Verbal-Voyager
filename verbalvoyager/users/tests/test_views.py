import pytest
from django.urls import reverse


@pytest.fixture
def data_with_wrong_fields():
    data = {
        'username': 'student_user',  # Already exists
        'password1': 'password',  # Too easy
        'password2': 'password',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@'  # Wrong format
    }
    return data


@pytest.fixture
def data_with_not_matched_passwords():
    data = {
        'username': 'new_username',
        'password1': 'password',  # Don't match
        'password2': 'password123',  # Don't match
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com'
    }
    return data


# Tests

@pytest.mark.django_db
def test_user_logout_with_redirect_home_page(client):
    url = reverse('logout')

    response = client.get(url, follow=False)
    assert response.status_code == 302

    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert '<title> Главная </title>' in response.content.decode()


@pytest.mark.django_db
def test_user_auth_get_success(client):
    url = reverse('auth')

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_auth_success_and_redirect(client, student_user):
    url = reverse('auth')
    data = {
        'login': 'student_user',
        'password': 'password'
    }

    response = client.post(url, data)
    assert response.status_code == 302
    assert client.session['_auth_user_id'] == str(student_user.id)

    response = client.post(url, data, follow=True)
    assert response.status_code == 200
    # TODO: check redirect url


@pytest.mark.django_db
def test_user_auth_fail(client, student_user):
    url = reverse('auth')
    data = {
        'login': student_user.username,
        'password': 'wrong password'
    }

    response = client.post(url, data)
    assert response.status_code == 200
    assert 'Неправильное имя пользователя или пароль' in response.content.decode()


@pytest.mark.django_db
def test_user_sign_up_success(
    client, 
    student_demo_group, 
    teacher_demo_group,
    teacher_demo_user,
    exercise_demo_category,
    exercise_english_word_with_category_demo,
    exercise_english_dialog_with_category_demo,
    exercise_irregular_verbs_with_category_demo
    ):
    url = reverse('auth')
    data = {
        'username': 'new_username',
        'password1': '0ifO-4Fuzw',
        'password2': '0ifO-4Fuzw',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com'
    }

    response = client.post(url, data)
    assert response.status_code == 302
    response = client.post(url, data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_sign_up_failed(client, student_user, data_with_wrong_fields, data_with_not_matched_passwords):
    url = reverse('auth')

    response = client.post(url, data_with_wrong_fields, follow=True)
    assert response.status_code == 200
    assert 'Пользователь с таким именем уже существует' in response.content.decode()
    assert 'Введённый пароль слишком широко распространён' in response.content.decode()
    assert 'Введите правильный адрес электронной почты' in response.content.decode()

    response = client.post(url, data_with_not_matched_passwords, follow=True)
    assert response.status_code == 200
    assert 'Введенные пароли не совпадают' in response.content.decode()


@pytest.mark.django_db
def test_user_reset_password_get_success(client):
    url = reverse('reset_password')

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_activities_groupless_user_account_success(groupless_user_client):
    url = reverse("account", kwargs={"current_pane": "activities"})
    response = groupless_user_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_activities_student_account_success(student_client):
    url = reverse("account", kwargs={"current_pane": "activities"})
    response = student_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_activities_teacher_account_success(teacher_client):
    url = reverse("account", kwargs={"current_pane": "activities"})
    response = teacher_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_activities_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "activities"})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_account_profile_groupless_user_account_success(groupless_user_client):
    url = reverse("account", kwargs={"current_pane": "profile"})
    response = groupless_user_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_profile_student_account_success(student_client):
    url = reverse("account", kwargs={"current_pane": "profile"})
    response = student_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_profile_teacher_account_success(teacher_client):
    url = reverse("account", kwargs={"current_pane": "profile"})
    response = teacher_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_profile_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "profile"})
    reponse = client.get(url)
    assert reponse.status_code == 302


@pytest.mark.django_db
def test_account_exercises_groupless_user_account_success(groupless_user_client):
    url = reverse("account", kwargs={"current_pane": "exercises"})
    response = groupless_user_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_exercises_student_account_success(student_client):
    url = reverse("account", kwargs={"current_pane": "exercises"})
    response = student_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_exercises_teacher_account_success(teacher_client):
    url = reverse("account", kwargs={"current_pane": "exercises"})
    response = teacher_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_exercises_anonimous_redirection(client):
    url = reverse("account", kwargs={"current_pane": "exercises"})
    response = client.get(url)
    assert response.status_code == 302
