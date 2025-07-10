import pytest
from conftest import check_all_static_files_in_templates, check_all_js_imports


@pytest.mark.django_db
def test_check_all_static_files_in_templates():
    missed_static = check_all_static_files_in_templates('exercises')

    if missed_static:
        print("\n" + "="*50)
        print("🚨 Обнаружены отсутствующие статические файлы в шаблонах:")
        print("="*50)

        for missing_file, referencing_templates in missed_static.items():
            print(f"\n🔴 Отсутствует файл: {missing_file}")
            print("📌 Используется в шаблонах:")
            for template_path in referencing_templates:
                print(f"   - {template_path}")

        print("\n" + "="*50)
        print(f"Всего отсутствует {len(missed_static)} файлов")
        print("="*50 + "\n")

    assert missed_static == {}, "Обнаружены отсутствующие статические файлы в шаблонах"


@pytest.mark.django_db
def test_check_all_js_imports():
    missed_js_imports = check_all_js_imports('exercises')

    if missed_js_imports:
        print("\n" + "="*50)
        print("🚨 Обнаружены отсутствующие JS-импорты:")
        print("="*50)

        for missing_file, referencing_files in missed_js_imports.items():
            print(f"\n🔴 Отсутствует файл: {missing_file}")
            print("📌 Используется в:")
            for js_path in referencing_files:
                print(f"   - {js_path}")

        print("\n" + "="*50)
        print(f"Всего отсутствует {len(missed_js_imports)} файлов")
        print("="*50 + "\n")

    assert missed_js_imports == {}, "Обнаружены отсутствующие JS-импорты"
