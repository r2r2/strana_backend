from admin_auto_filters.filters import AutocompleteFilter


class AutocompleteAgenciesFilter(AutocompleteFilter):
    title = "Агентство"
    field_name = "agency"

