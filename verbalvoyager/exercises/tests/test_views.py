import pytest
from django.urls import reverse
from django.contrib.auth.models import Group
from dictionary.models import EnglishWord, FrenchWord, IrregularEnglishVerb
from exercises.models import ExerciseEnglishWords, ExerciseEnglishDialog, \
    ExerciseIrregularEnglishVerb, ExerciseFrenchWords, ExerciseFrenchDialog


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
def another_student_user(django_user_model):
    student_user = django_user_model.objects.create(
        username='another_student_user',
        email='another_student_user@mail.com',
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


@pytest.fixture
def english_words():
    word_1 = EnglishWord.objects.create(
        word='abandon',
        translation='оставлять',
        examples="['We had to [abandon] the car.', 'His mother [abandoned] him when he was five days old.', 'We [abandoned] the old car in the empty parking lot.', 'He claimed that his parents had [abandoned] him.']",
        image_url='http://cdn-user77752.skyeng.ru/skyconvert/unsafe/640x480/https://cdn-user77752.skyeng.ru/images/9673f89d558855ab30a3bbf7740d7a6b.jpeg',
        sound_url='https://vimbox-tts.skyeng.ru/api/v1/tts?text=%3Cspeak%3E%3Cphoneme+alphabet%3D%22ipa%22+ph%3D%22əˈbændən%22%3E%3C%2Fphoneme%3E%3C%2Fspeak%3E&lang=en&voice=female_2&isSsml=1',
        speech_code='verb',
        definition='To leave a thing or a person permanently or for a long time.',
        prefix='to',
        transcription='əˈbændən'
    )
    word_2 = EnglishWord.objects.create(
        word='back up',
        translation='поддерживать',
        examples="['They [backed] me [up] at the meeting.', 'They asked local administrators to [back] them [up].', 'If I ask for more money will you [back] me [up]?']",
        image_url='//cdn-user77752.skyeng.ru/skyconvert/unsafe/640x480/https://cdn-user77752.skyeng.ru/images/d1ed6804ccbf1be5e639b3e0b7415d00.png',
        sound_url='https://vimbox-tts.skyeng.ru/api/v1/tts?text=back+up&lang=en&voice=female_2',
        speech_code='verb',
        definition="To show someone's support for someone else.",
        prefix='to',
        transcription='bæk ʌp'
    )
    word_3 = EnglishWord.objects.create(
        word='deal',
        translation='выгодная покупка',
        examples="""['We found an incredible [deal] on a holiday package to Hawaii.', "I couldn't believe the[deal] I got on those sneakers."]""",
        image_url='',
        sound_url='https://vimbox-tts.skyeng.ru/api/v1/tts?text=deal&lang=en&voice=female_2',
        speech_code='noun',
        definition='Bargain; price that is lower than usual.',
        prefix='to',
        transcription='diːl'
    )
    return word_1, word_2, word_3


@pytest.fixture
def irregular_words():
    word_1 = EnglishWord.objects.create(
        word='arise',
        translation='возникать'
    )
    word_2 = EnglishWord.objects.create(
        word='awake',
        translation='будить'
    )
    word_3 = EnglishWord.objects.create(
        word='beat',
        translation='стучать'
    )
    return word_1, word_2, word_3


@pytest.fixture
def irregular_verbs(irregular_words):
    word_1, word_2, word_3 = irregular_words
    verb_1 = IrregularEnglishVerb.objects.create(
        infinitive=word_1,
        past_simple='arose',
        past_participle='arisen'
    )
    verb_2 = IrregularEnglishVerb.objects.create(
        infinitive=word_2,
        past_simple='awoke',
        past_participle='awoken'
    )
    verb_3 = IrregularEnglishVerb.objects.create(
        infinitive=word_3,
        past_simple='beat',
        past_participle='beaten'
    )
    return verb_1, verb_2, verb_3


@pytest.fixture
def exercise_irregular_verbs(irregular_verbs, student_user, teacher_user):
    exercise = ExerciseIrregularEnglishVerb.objects.create(
        name='Irregular Verb 1',
        student=student_user,
        teacher=teacher_user,
    )
    exercise.words.set(irregular_verbs)
    return exercise


@pytest.fixture
def exercise_irregular_verbs_with_external_access(irregular_verbs, student_user, teacher_user):
    exercise = ExerciseIrregularEnglishVerb.objects.create(
        name='Irregular Verb 2',
        student=student_user,
        teacher=teacher_user,
        external_access=True
    )
    exercise.words.set(irregular_verbs)
    return exercise


@pytest.fixture
def exercise_english_words(english_words, student_user, teacher_user):
    exercise = ExerciseEnglishWords.objects.create(
        name='Words 1',
        student=student_user,
        teacher=teacher_user,
    )
    exercise.words.set(english_words)
    return exercise


@pytest.fixture
def exercise_english_words_with_exernal_access(english_words, student_user, teacher_user):
    exercise = ExerciseEnglishWords.objects.create(
        name='Words 2',
        student=student_user,
        teacher=teacher_user,
        external_access=True
    )
    exercise.words.set(english_words)
    return exercise


@pytest.fixture
def exercise_english_dialogs(english_words, student_user, teacher_user):
    exercise = ExerciseEnglishDialog.objects.create(
        name='Dialog 1',
        student=student_user,
        teacher=teacher_user,
        text="""Situation: Two friends, Tom and Mike, are cleaning up Tom's room together.

            Tom: Mike, can you back me up with this big box? It’s too heavy for me.  
            Mike: Sure, Tom! I’ll help. Where do you want to put it?  

            Tom: Let’s move it to the corner. My mom said we can’t abandon it in the middle of the room.  
            Mike: Okay, deal. I’ll take this side. You take the other side.  

            Tom: Thanks, Mike. You’re a good friend. I’ll buy you a snack later, deal?  
            Mike: Deal! But first, let’s finish cleaning.  

            Tom: Alright, after we’re done, I’ll back you up with your math homework.  
            Mike: Perfect! You’re the best, Tom!  

            Tom: Thanks, Mike. Friends always help each other, right?  
            Mike: Right! Let’s get this done quickly!"""
    )
    exercise.words.set(english_words)
    return exercise


@pytest.fixture
def exercise_english_dialogs_with_exernal_access(english_words, student_user, teacher_user):
    exercise = ExerciseEnglishDialog.objects.create(
        name='Dialog 2',
        student=student_user,
        teacher=teacher_user,
        text="""Situation: Two friends, Tom and Mike, are cleaning up Tom's room together.

        Tom: Mike, can you back me up with this big box? It’s too heavy for me.  
        Mike: Sure, Tom! I’ll help. Where do you want to put it?  

        Tom: Let’s move it to the corner. My mom said we can’t abandon it in the middle of the room.  
        Mike: Okay, deal. I’ll take this side. You take the other side.  

        Tom: Thanks, Mike. You’re a good friend. I’ll buy you a snack later, deal?  
        Mike: Deal! But first, let’s finish cleaning.  

        Tom: Alright, after we’re done, I’ll back you up with your math homework.  
        Mike: Perfect! You’re the best, Tom!  

        Tom: Thanks, Mike. Friends always help each other, right?  
        Mike: Right! Let’s get this done quickly!""",
        external_access=True
    )
    exercise.words.set(english_words)
    return exercise


# Tests

# EnglishWords
@pytest.mark.django_db
def test_exercise_english_words_success(exercise_english_words, client, student_user):
    client.force_login(student_user)
    url = reverse(
        'exercise_words',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_words.pk,
            'step': 1
        }
    )

    assert client.get(url).status_code == 200


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
def test_exercise_english_dialogs_success(exercise_english_dialogs, client, student_user):
    client.force_login(student_user)
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialogs.pk,
        }
    )

    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_exercise_english_dialogs_redirect(exercise_english_dialogs, client):
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialogs.pk,
        }
    )

    assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_exercise_english_dialogs_words_not_found(exercise_english_dialogs, client, another_student_user):
    client.force_login(another_student_user)
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialogs.pk,
        }
    )

    assert client.get(url).status_code == 404


@pytest.mark.django_db
def test_exercise_english_dialogs_with_exeternal_access_success(exercise_english_dialogs_with_exernal_access, client):
    url = reverse(
        'exercise_dialog',
        kwargs={
            'ex_lang': 'english',
            'ex_id': exercise_english_dialogs_with_exernal_access.pk,
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
