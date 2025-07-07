import pytest
from conftest import check_all_static_files_in_templates


@pytest.mark.django_db
def test_check_all_static_files_in_templates():
    assert check_all_static_files_in_templates('pages') == {}
