import pytest
from django.contrib.auth.models import Group
from users.models import User


@pytest.mark.django_db
def test_user_creation():
    """
    Test that a User can be created and saved to the database.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
    assert user.check_password('testpassword123')


@pytest.mark.django_db
def test_user_str_method():
    """
    Test the __str__ method of the User model.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    assert str(user) == 'testuser'

    user.first_name = 'John'
    user.last_name = 'Doe'
    user.save()
    assert str(user) == 'Doe John'


@pytest.mark.django_db
def test_user_timezone_default():
    """
    Test that the default timezone is set correctly.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    assert user.timezone == 'Europe/Saratov'


@pytest.mark.django_db
def test_user_is_teacher():
    """
    Test the is_teacher method of the User model.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    teacher_group = Group.objects.get(name='Teacher')
    user.groups.add(teacher_group)

    assert user.is_teacher()


@pytest.mark.django_db
def test_user_is_student():
    """
    Test the is_student method of the User model.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    student_group = Group.objects.get(name='Student')
    user.groups.add(student_group)

    assert user.is_student()


@pytest.mark.django_db
def test_user_is_supervisor():
    """
    Test the is_supervisor method of the User model.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    supervisor_group = Group.objects.get(name='Supervisor')
    user.groups.add(supervisor_group)

    assert user.is_supervisor()


@pytest.mark.django_db
def test_user_get_groups():
    """
    Test the get_groups method of the User model.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword123', email='testuser@example.com')
    teacher_group = Group.objects.get(name='Teacher')
    student_group = Group.objects.get(name='Student')
    user.groups.add(teacher_group, student_group)

    groups = user.get_groups()
    assert len(groups) == 2
    assert 'Teacher' in [group.name for group in groups]
    assert 'Student' in [group.name for group in groups]


@pytest.mark.django_db
def test_user_get_teachers():
    """
    Test the get_teachers method of the User model.
    """
    teacher_group = Group.objects.get(name='Teacher')
    teacher1 = User.objects.create_user(
        username='teacher1', password='testpassword123', email='teacher1@example.com')
    teacher2 = User.objects.create_user(
        username='teacher2', password='testpassword123', email='teacher2@example.com')
    teacher1.groups.add(teacher_group)
    teacher2.groups.add(teacher_group)

    teachers = User.objects.filter(groups__name__in=['Teacher'])
    assert len(teachers) == 2
    assert 'teacher1' in [teacher.username for teacher in teachers]
    assert 'teacher2' in [teacher.username for teacher in teachers]


@pytest.mark.django_db
def test_user_get_students():
    """
    Test the get_students method of the User model.
    """
    student_group = Group.objects.get(name='Student')
    student1 = User.objects.create_user(
        username='student1', password='testpassword123', email='student1@example.com')
    student2 = User.objects.create_user(
        username='student2', password='testpassword123', email='student2@example.com')
    student1.groups.add(student_group)
    student2.groups.add(student_group)

    students = User.objects.filter(groups__name__in=['Student'])
    assert len(students) == 2
    assert 'student1' in [student.username for student in students]
    assert 'student2' in [student.username for student in students]
