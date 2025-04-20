import pytest
from django.urls import reverse

# EnglishWords


@pytest.mark.django_db
def test_exercise_english_words_success(exercise_english_words, student_client):
    url = reverse(
        'exercise_words',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_words.pk,
            'step': 1
        }
    )

    assert student_client.get(url).status_code == 200


@pytest.mark.django_db
def test_exercise_english_words_redirect(exercise_english_words, client):
    url = reverse(
        'exercise_words',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_words.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_exercise_english_words_not_found(exercise_english_words, client, another_student_user):
    client.force_login(another_student_user)
    url = reverse(
        'exercise_words',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_words.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 404


@pytest.mark.django_db
def test_exercise_english_words_with_exeternal_access_success(exercise_english_words_with_exernal_access, client):
    url = reverse(
        'exercise_words',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_words_with_exernal_access.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 200

# EnglishDialogs


@pytest.mark.django_db
def test_exercise_english_dialogs_success(exercise_english_dialog, client, student_user):
    client.force_login(student_user)
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialog.pk,
        }
    )

    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_exercise_english_dialogs_redirect(exercise_english_dialog, client):
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialog.pk,
        }
    )

    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_exercise_english_dialogs_words_not_found(exercise_english_dialog, client, another_student_user):
    client.force_login(another_student_user)
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialog.pk,
        }
    )

    assert client.get(url).status_code == 404


@pytest.mark.django_db
def test_exercise_english_dialogs_with_exeternal_access_success(exercise_english_dialog_with_exernal_access, client):
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialog_with_exernal_access.pk,
        }
    )

    assert client.get(url).status_code == 200

# Irregular Verbs


@pytest.mark.django_db
def test_exercise_irregular_verbs_success(exercise_irregular_verbs, client, student_user):
    client.force_login(student_user)
    url = reverse(
        'exercise_irregular_verbs',
        kwargs={
            'ex_id': exercise_irregular_verbs.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_exercise_irregular_verbs_redirect(exercise_irregular_verbs, client):
    url = reverse(
        'exercise_irregular_verbs',
        kwargs={
            'ex_id': exercise_irregular_verbs.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_exercise_irregular_verbs_not_found(exercise_irregular_verbs, client, another_student_user):
    client.force_login(another_student_user)
    url = reverse(
        'exercise_irregular_verbs',
        kwargs={
            'ex_id': exercise_irregular_verbs.pk,
            'step': 1

        }
    )

    assert client.get(url).status_code == 404


@pytest.mark.django_db
def test_exercise_irregular_verbs_with_exeternal_access_success(exercise_irregular_verbs_with_external_access, client):
    url = reverse(
        'exercise_irregular_verbs',
        kwargs={
            'ex_id': exercise_irregular_verbs_with_external_access.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 200
