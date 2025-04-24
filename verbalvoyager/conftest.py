import pytest
from django.test import Client
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite


from dictionary.models import EnglishWord, IrregularEnglishVerb
from exercises.models import ExerciseCategory, ExerciseEnglishWords, ExerciseEnglishDialog, \
    ExerciseIrregularEnglishVerb


User = get_user_model()


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def admin_user():
    return User.objects.create_superuser('admin', 'admin@admin.com', 'admin_password')


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def student_group():
    group, _ = Group.objects.get_or_create(name='Student')
    return group

@pytest.fixture
def student_demo_group():
    group, _ = Group.objects.get_or_create(name='StudentDemo')
    return group


@pytest.fixture
def teacher_group():
    group, _ = Group.objects.get_or_create(name='Teacher')
    return group

@pytest.fixture
def teacher_demo_group():
    group, _ = Group.objects.get_or_create(name='TeacherDemo')
    return group


@pytest.fixture
def groupless_user(django_user_model):
    user = django_user_model.objects.create(
        username='groupless_user',
        email='groupless_user@mail.com',
        password='password'
    )
    return user


@pytest.fixture
def groupless_user_client(groupless_user):
    client = Client()
    client.force_login(groupless_user)
    return client


@pytest.fixture
def student_user(django_user_model, student_group):
    user = django_user_model.objects.create_user(
        username='student_user',
        email='student_user@mail.com',
        password='password'
    )
    user.groups.add(student_group)

    return user


@pytest.fixture
def student_client(student_user):
    client = Client()
    client.force_login(student_user)
    return client


@pytest.fixture
def another_student_user(django_user_model):
    user = django_user_model.objects.create_user(
        username='another_student_user',
        email='another_student_user@mail.com',
        password='password'
    )
    return user


@pytest.fixture
def another_student_client(another_student_user):
    client = Client()
    client.force_login(another_student_user)
    return client


@pytest.fixture
def teacher_user(django_user_model, teacher_group):
    user = django_user_model.objects.create_user(
        username='teacher_user',
        email='teacher_user@mail.com',
        password='password'
    )
    user.groups.add(teacher_group)
    return user

@pytest.fixture
def teacher_demo_user(django_user_model, teacher_demo_group):
    user = django_user_model.objects.create_user(
        username='demo_teacher',
        email='demo@teacher.ru',
        password='password'
    )
    user.groups.add(teacher_demo_group)
    return user

@pytest.fixture
def teacher_client(teacher_user):
    client = Client()
    client.force_login(teacher_user)
    return client

# @pytest.fixture
# def exercise_english_words_model():
#     return ExerciseEnglishWords

# @pytest.fixture
# def exercise_irregular_english_verb_model():
#     return ExerciseIrregularEnglishVerb

# @pytest.fixture
# def exercise_english_dialog_model():
#     return ExerciseEnglishDialog

@pytest.fixture
def exercise_demo_category():
    category, _ = ExerciseCategory.objects.get_or_create(
        name='Demo'
    )
    return category


@pytest.fixture
def english_words():
    word_1, _ = EnglishWord.objects.get_or_create(
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
    word_2, _ = EnglishWord.objects.get_or_create(
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
    word_3, _ = EnglishWord.objects.get_or_create(
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
    word_1, _ = EnglishWord.objects.get_or_create(
        word='arise',
        translation='возникать'
    )
    word_2, _ = EnglishWord.objects.get_or_create(
        word='awake',
        translation='будить'
    )
    word_3, _ = EnglishWord.objects.get_or_create(
        word='beat',
        translation='стучать'
    )
    return word_1, word_2, word_3


@pytest.fixture
def irregular_verbs(irregular_words):
    word_1, word_2, word_3 = irregular_words
    verb_1, _ = IrregularEnglishVerb.objects.get_or_create(
        infinitive=word_1,
        past_simple='arose',
        past_participle='arisen'
    )
    verb_2, _ = IrregularEnglishVerb.objects.get_or_create(
        infinitive=word_2,
        past_simple='awoke',
        past_participle='awoken'
    )
    verb_3, _ = IrregularEnglishVerb.objects.get_or_create(
        infinitive=word_3,
        past_simple='beat',
        past_participle='beaten'
    )
    return verb_1, verb_2, verb_3


@pytest.fixture
def exercise_irregular_verbs(irregular_verbs, student_user, teacher_user):
    exercise, _ = ExerciseIrregularEnglishVerb.objects.get_or_create(
        name='Irregular Verb 1',
        student=student_user,
        teacher=teacher_user,
    )
    exercise.words.set(irregular_verbs)
    return exercise


@pytest.fixture
def exercise_irregular_verbs_with_external_access(irregular_verbs, student_user, teacher_user):
    exercise, _ = ExerciseIrregularEnglishVerb.objects.get_or_create(
        name='Irregular Verb 2',
        student=student_user,
        teacher=teacher_user,
        external_access=True
    )
    exercise.words.set(irregular_verbs)
    return exercise

@pytest.fixture
def exercise_irregular_verbs_with_category_demo(irregular_verbs, student_user, teacher_user, exercise_demo_category):
    exercise, _ = ExerciseIrregularEnglishVerb.objects.get_or_create(
        name='Demo Exercise',
        student=student_user,
        teacher=teacher_user,
        category=exercise_demo_category
    )
    
    exercise.category = exercise_demo_category
    exercise.words.set(irregular_verbs)
    return exercise

@pytest.fixture
def exercise_english_words(english_words, student_user, teacher_user):
    exercise, _ = ExerciseEnglishWords.objects.get_or_create(
        name='Words 1',
        student=student_user,
        teacher=teacher_user,
    )
    exercise.words.set(english_words)
    return exercise


@pytest.fixture
def exercise_english_words_with_exernal_access(english_words, student_user, teacher_user):
    exercise, _ = ExerciseEnglishWords.objects.get_or_create(
        name='Words 2',
        student=student_user,
        teacher=teacher_user,
        external_access=True
    )
    exercise.words.set(english_words)
    return exercise


@pytest.fixture
def exercise_english_word_with_category_demo(english_words, student_user, teacher_user, exercise_demo_category):
    exercise, _ = ExerciseEnglishWords.objects.get_or_create(
        name='Demo Exercise',
        student=student_user,
        teacher=teacher_user,
        category=exercise_demo_category
    )
    
    exercise.words.set(english_words)

    return exercise

@pytest.fixture
def exercise_english_dialog(english_words, student_user, teacher_user):
    exercise, _ = ExerciseEnglishDialog.objects.get_or_create(
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
def exercise_english_dialog_with_exernal_access(english_words, student_user, teacher_user, exercise_demo_category):
    exercise, _ = ExerciseEnglishDialog.objects.get_or_create(
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

@pytest.fixture
def exercise_english_dialog_with_category_demo(english_words, student_user, teacher_user, exercise_demo_category):
    exercise, _ = ExerciseEnglishDialog.objects.get_or_create(
        name='Demo Exercise',
        student=student_user,
        teacher=teacher_user,
        category=exercise_demo_category
    )
    
    exercise.category = exercise_demo_category
    exercise.words.set(english_words)
    return exercise