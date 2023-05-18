from django.forms.widgets import (
    MultiWidget,
    TextInput,
    HiddenInput,
    Textarea,
    SelectMultiple,
)


class PpoiWidget(MultiWidget):
    template_name = "common/widgets/ppoi.html"

    def __init__(self, attrs=None):
        _widgets = (TextInput(attrs=attrs), HiddenInput(attrs=attrs))
        super().__init__(widgets=_widgets, attrs={"class": "PpoiField__input", **(attrs or {})})

    def decompress(self, value):
        if value is None:
            return []
        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

    class Media:
        css = {"screen": ("common/css/ppoi-widget.css",)}
        js = ("common/js/ppoi-widget.js",)


class PolygonWidget(MultiWidget):
    template_name = "common/widgets/polygon.html"

    def __init__(self, attrs=None):
        _widgets = (
            Textarea(attrs=attrs),
            HiddenInput(attrs=attrs),
            HiddenInput(attrs=attrs),
            HiddenInput(attrs=attrs),
        )
        super().__init__(widgets=_widgets, attrs={"class": "js-sc-i", **(attrs or {})})

    def decompress(self, value):
        if value is None:
            return []
        return value

    class Media:
        css = {"screen": ("common/css/polygon-widget.css",)}
        js = ("common/js/polygon-widget.js",)


class ArraySelectMultiple(SelectMultiple):
    def value_omitted_from_data(self, data, files, name):
        return False
