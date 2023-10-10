from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import Building, BuildingBookingType


class BookingTypesForm(forms.ModelForm):
    booking_types = forms.ModelMultipleChoiceField(
        label="Типы бронирований",
        queryset=BuildingBookingType.objects.all(),
        widget=FilteredSelectMultiple("типы", True),
    )

    def __init__(self, *args, **kwargs):
        super(BookingTypesForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["booking_types"].initial = self.instance.booking_types.all()

    def save(self, commit=True):
        if booking_types := self.cleaned_data.get("booking_types"):
            self.instance.booking_types.set(booking_types)
            self.instance.save()
        return super().save()

    def save_m2m(self):
        super()._save_m2m()

    class Meta:
        model = BuildingBookingType
        fields = "__all__"


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    search_fields = ("name", "project__name")
    list_display = ("name", "project", "global_id")
    form = BookingTypesForm
