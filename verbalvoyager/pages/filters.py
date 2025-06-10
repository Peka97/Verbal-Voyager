from django.contrib.admin import SimpleListFilter, AllValuesFieldListFilter, ChoicesFieldListFilter, RelatedFieldListFilter, RelatedOnlyFieldListFilter


DROPDOWN_TEMPLATE_PATH = 'pages/admin/dropdown_filter.html'


class SimpleDropdownFilter(SimpleListFilter):
    template = DROPDOWN_TEMPLATE_PATH


class DropdownFilter(AllValuesFieldListFilter):
    template = DROPDOWN_TEMPLATE_PATH


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = DROPDOWN_TEMPLATE_PATH


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = DROPDOWN_TEMPLATE_PATH


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = DROPDOWN_TEMPLATE_PATH
