if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verbalvoyager.settings')
    django.setup()
    from dictionary.models import Translation, RussianWordDetail, Language
    from django.core.exceptions import ValidationError

    ru_details = RussianWordDetail.objects.all()

    for ru_detail in ru_details:
        translation_qs = Translation.objects.filter(target_word=ru_detail.word)

        if not translation_qs.exists():
            continue

        for translation in translation_qs.all():
            translation.image_url = ru_detail.image_url
            try:
                translation.save()
            except ValidationError:
                print(f'Error with {translation.pk}')
