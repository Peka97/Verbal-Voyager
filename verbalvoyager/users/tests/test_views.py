import pytest
from django.urls import reverse

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group

from django.test import TestCase, Client


# Fixtures

User = get_user_model()


# Tests


class AuthenticationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('auth')
        self.success_url = reverse('')
        self.logout_url = reverse('logout')
        self.username = 'student_user'
        self.password = 'password'
        self.user = User.objects.create_user(
            username=self.username, password=self.password)

    def test_login_page_exists(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)

    def test_successful_login_redirects(self):
        response = self.client.post(
            self.login_url, {'login': self.username, 'password': self.password})

        self.assertEqual(response.status_code, 302)  # Ожидаем код 302 Redirect
        self.assertRedirects(response, self.success_url)
        self.assertTrue(response.client.session['_auth_user_id'])

    def test_successful_login_user_is_authenticated(self):
        self.client.post(self.login_url, {
                         'login': self.username, 'password': self.password})
        user = authenticate(username=self.username, password=self.password)

        self.assertTrue(user.is_authenticated)

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            self.login_url,
            {'login': self.username, 'password': 'wrongpassword'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Неправильное имя пользователя или пароль",
                      response.content.decode('utf-8'))
        self.assertFalse(response.client.session.get('_auth_user_id', False))

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.logout_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.success_url, self.client.session)


class AccountPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.activities_page = reverse(
            'account', kwargs={'current_pane': 'activities'})
        self.profile_page = reverse(
            'account', kwargs={'current_pane': 'profile'})
        self.exercises_page = reverse(
            'account', kwargs={'current_pane': 'exercises'})
        self.user = User.objects.create_user(
            username='test_user', password='test_password')

        self.student_group, _ = Group.objects.get_or_create(name='Student')
        self.teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        self.student = User.objects.create_user(
            username='test_student', password='test_password')
        self.teacher = User.objects.create_user(
            username='test_teacher', password='test_password')
        self.student.groups.add(self.student_group)
        self.teacher.groups.add(self.teacher_group)

    def test_login_required_account_page(self):
        self.client.logout()
        response = self.client.get(self.activities_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.profile_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.exercises_page)
        self.assertEqual(response.status_code, 302)

    def test_activities_page_success_with_base_user(self):
        self.client.login(username=self.user.username,
                          password=self.user.password)
        response = self.client.get(self.activities_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_profile_page_success_with_base_user(self):
        self.client.login(username=self.user.username,
                          password=self.user.password)
        response = self.client.get(self.profile_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_exercises_page_success_with_base_user(self):
        self.client.login(username=self.user.username,
                          password=self.user.password)
        response = self.client.get(self.exercises_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_activities_page_success_with_student(self):
        self.client.login(username=self.student.username,
                          password=self.student.password)
        response = self.client.get(self.activities_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_profile_page_success_with_student(self):
        self.client.login(username=self.student.username,
                          password=self.student.password)
        response = self.client.get(self.profile_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_exercises_page_success_with_student(self):
        self.client.login(username=self.student.username,
                          password=self.student.password)
        response = self.client.get(self.exercises_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_activities_page_success_with_teacher(self):
        self.client.login(username=self.teacher.username,
                          password=self.teacher.password)
        response = self.client.get(self.activities_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_profile_page_success_with_teacher(self):
        self.client.login(username=self.teacher.username,
                          password=self.teacher.password)
        response = self.client.get(self.profile_page, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_exercises_page_success_with_teacher(self):
        self.client.login(username=self.teacher.username,
                          password=self.teacher.password)
        response = self.client.get(self.exercises_page, follow=True)
        self.assertEqual(response.status_code, 200)


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
