from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict
from django.contrib.admin.widgets import FilteredSelectMultiple



class FilteredSelectOneToOne(FilteredSelectMultiple):
    """
    Виджет выбора с поиском для O2O
    """
    def __init__(self, verbose_name: str = "(только 1)", is_stacked: bool = False, *args, **kwargs):
        super().__init__(verbose_name, is_stacked, *args, **kwargs)

    def value_from_datadict(self, data: QueryDict, files: MultiValueDict, name: str) -> str:
        getter = data.get
        values: list[str] = super().value_from_datadict(data, files, name)
        if values and len(values) > 1:
            try:
                getter = data.getlist
            except AttributeError:
                pass
        return getter(name)
