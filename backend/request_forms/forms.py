import binascii

from django.core.exceptions import ValidationError
from django.forms import (CharField, EmailField, Form, IntegerField,
                          ModelChoiceField, ModelForm, URLField)
from graphql_relay import from_global_id
from phonenumber_field.formfields import PhoneNumberField

from buildings.models import BuildingBookingType
from contacts.models import Office
from landing.models import Landing, LandingBlock
from main_page.models import MainPageSlide
from news.models import News
from projects.models import Project
from properties.constants import PropertyType
from properties.models import Property

from .models import *

__all__ = [
    "NewsRequestForm",
    "SaleRequestForm",
    "OfficeRequestForm",
    "AgentRequestForm",
    "NameAndPhoneForm",
    "MediaRequestForm",
    "LotCardRequestForm",
    "LandingRequestForm",
    "CustomRequestForm",
    "TeaserRequestForm",
    "AntiCorruptionForm",
    "VacancyRequestForm",
    "StartSaleRequestForm",
    "ContractorRequestForm",
    "CustomFormEmployeeForm",
    "PropertyAndProjectForm",
    "NamePhoneAndProjectForm",
    "NewsletterSubscriptionForm",
    "DirectorCommunicateRequestForm",
    "CallbackRequestForm",
    "PresentationRequestForm",
    "CommercialKotelnikiRequestForm",
    "BeFirstRequestModelForm",
    "AdvantageFormRequestModelForm",
]


def validate_charfield(value):
    forbidden_symbols = '[!#$%^&*()/\"\'№;:?<>]'
    if any(v in forbidden_symbols for v in value):
        raise ValidationError("Запрещенные символы в форме")


class SaleRequestForm(ModelForm):
    email = EmailField(required=True)

    class Meta:
        model = SaleRequest
        exclude = ("id", "date")


class MediaRequestForm(ModelForm):
    email = EmailField(required=True)
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    comment = CharField(required=True, max_length=2000, validators=[validate_charfield])
    media_name = CharField(required=False, max_length=250, validators=[validate_charfield])

    class Meta:
        model = MediaRequest
        exclude = ("id", "date")


class VacancyRequestForm(ModelForm):
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})

    class Meta:
        model = VacancyRequest
        exclude = ("id", "resume", "date")


class NameAndPhoneForm(Form):
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})


class NamePhoneAndProjectForm(Form):
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    project_slug = CharField(required=False, max_length=400, validators=[validate_charfield])
    property_type = CharField(required=False, max_length=100, validators=[validate_charfield])
    property = CharField(required=False, max_length=100, validators=[validate_charfield])
    booking_type = CharField(required=False, max_length=100, validators=[validate_charfield])

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug

    def clean_property_type(self):
        value = self.cleaned_data.get("property_type")
        if value and value not in PropertyType.values:
            raise ValidationError("Invalid property type")
        return value

    def clean_property(self):
        value = self.cleaned_data.get("property")
        if value and not Property.objects.filter(id=value).exists():
            raise ValidationError("Invalid property")
        return value

    def clean_booking_type(self):
        value = self.cleaned_data.get("booking_type")
        if value and not BuildingBookingType.objects.filter(id=value).exists():
            raise ValidationError("Invalid booking type")
        return value


class PropertyAndProjectForm(Form):
    project_slug = CharField(required=True, max_length=400, validators=[validate_charfield])
    property_type = CharField(required=True, max_length=100, validators=[validate_charfield])
    property = CharField(required=True, max_length=100, validators=[validate_charfield])

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug

    def clean_property_type(self):
        value = self.cleaned_data.get("property_type")
        if value and value not in PropertyType.values:
            raise ValidationError("Invalid property type")
        return value

    def clean_property(self):
        _, value = from_global_id(self.cleaned_data.get("property"))
        if value and not Property.objects.filter(id=value).exists():
            raise ValidationError("Invalid property")
        return value


class NewsletterSubscriptionForm(Form):
    email = EmailField(error_messages={'invalid': 'Электронный адрес введён неверно'})


class DirectorCommunicateRequestForm(NamePhoneAndProjectForm):
    email = EmailField(required=False)
    text = CharField(required=True, validators=[validate_charfield])


class CustomRequestForm(NamePhoneAndProjectForm):
    form = IntegerField(required=True)
    property_id = CharField(required=False, max_length=100, validators=[validate_charfield])

    def clean_form(self):
        form = self.cleaned_data.get("form")
        if form and not CustomForm.objects.filter(active=True, id=form).exists():
            raise ValidationError("Form not found")
        return form

    def clean_property_id(self):
        value = self.cleaned_data.get("property_id")
        if value:
            try:
                _, value = from_global_id(value)
            except (UnicodeDecodeError, binascii.Error, ValueError):
                raise ValidationError("Incorrect id")
            if not Property.objects.filter(id=value).exists():
                raise ValidationError("Property not found")
        return value


class CustomFormEmployeeForm(ModelForm):
    class Meta:
        model = CustomFormEmployee
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        self.check_project_in_city(cleaned_data)

    @staticmethod
    def check_project_in_city(data):
        city = data.get("city")
        project = data.get("project")
        if not project:
            return
        if not Project.objects.filter(id=project.id, city=city).exists():
            raise ValidationError("Нет такого проекта в городе.")


class AgentRequestForm(NameAndPhoneForm):
    city_name = CharField(required=True, max_length=64, validators=[validate_charfield])
    agency_name = CharField(required=True, max_length=100, validators=[validate_charfield])

    class Meta:
        model = AgentRequest


class ContractorRequestForm(NameAndPhoneForm):
    type_of_job = CharField(required=True, max_length=100, validators=[validate_charfield])
    about_company = CharField(required=True, validators=[validate_charfield])

    class Meta:
        model = ContractorRequest
        exclude = ("id", "offer", "date")


class LandingRequestForm(ModelForm):
    email = EmailField(required=False)
    name = CharField(max_length=32, validators=[validate_charfield])
    phone = PhoneNumberField(error_messages={'invalid': 'Телефон введён неверно'})
    block = IntegerField()
    landing = IntegerField(required=False)

    def clean_block(self):
        block_id = self.cleaned_data.get("block")

        block = LandingBlock.objects.filter(id=block_id).first()
        if not block:
            raise ValidationError("Block not found")
        return block

    def clean_landing(self):
        block_id = self.cleaned_data.get("block")
        if block_id:
            return Landing.objects.filter(landingblock=block_id).first()

    class Meta:
        model = LandingRequest
        exclude = ("id", "date")


class AntiCorruptionForm(ModelForm):
    class Meta:
        model = AntiCorruptionRequest
        exclude = ("id", "date")


class TeaserRequestForm(NamePhoneAndProjectForm):
    related_object = ModelChoiceField(queryset=MainPageSlide.objects.all())


class NewsRequestForm(NamePhoneAndProjectForm):
    related_object = CharField(validators=[validate_charfield])

    def clean_related_object(self):
        _, obj_id = from_global_id(self.cleaned_data.get("related_object"))
        return News.objects.filter(id=obj_id).first()


class OfficeRequestForm(NamePhoneAndProjectForm):
    related_object = CharField()

    def clean_related_object(self):
        _, obj_id = from_global_id(self.cleaned_data.get("related_object"))
        return Office.objects.filter(id=obj_id).first()


class LotCardRequestForm(Form):
    phone = PhoneNumberField(error_messages={'invalid': 'Телефон введён неверно'})
    interval = CharField(max_length=64, validators=[validate_charfield])
    related_object = CharField(validators=[validate_charfield])

    def clean_related_object(self):
        _, obj_id = from_global_id(self.cleaned_data.get("related_object"))
        return Property.objects.filter(id=obj_id).first()


class StartSaleRequestForm(Form):
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    email = EmailField(required=True)
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    project_slug = CharField(required=True, max_length=400, validators=[validate_charfield])
    property_type = CharField(required=True, max_length=100, validators=[validate_charfield])

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug

    def clean_property_type(self):
        value = self.cleaned_data.get("property_type")
        if value and value not in PropertyType.values:
            raise ValidationError("Invalid property type")
        return value


class StartProjectsRequestForm(Form):
    """Форма отклика старта проекта"""
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    email = EmailField(required=True)
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    project_slug = CharField(required=True, max_length=400, validators=[validate_charfield])
    applicant = CharField(required=True)

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug


class EKBStartSaleRequestForm(Form):
    """Форма уведомления о старте продаж: ЕКБ."""
    name = CharField(required=False, max_length=200, validators=[validate_charfield])
    email = EmailField(required=True)
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    applicant = CharField(required=True)


class CallbackRequestForm(Form):
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    interval = CharField(required=True)
    timezone_user = CharField(max_length=25)


class PresentationRequestForm(ModelForm):
    project_slug = CharField(required=True, max_length=400, validators=[validate_charfield])

    class Meta:
        model = PresentationRequest
        exclude = ("id", "date")

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug

    def clean_project(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return Project.objects.filter(slug=slug).last()


class CommercialKotelnikiRequestForm(Form):
    name = CharField(required=True, max_length=200, validators=[validate_charfield])
    phone = PhoneNumberField(required=True, error_messages={'invalid': 'Телефон введён неверно'})
    from_url = URLField(required=True)


class BeFirstRequestModelForm(ModelForm):
    class Meta:
        model = BeFirstRequest
        fields = ["email", "subdomain"]


class AdvantageFormRequestModelForm(ModelForm):
    project_slug = CharField(required=True, max_length=400, validators=[validate_charfield])

    class Meta:
        model = AdvantageFormRequest
        exclude = ("id", "date")

    def clean_project_slug(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return slug

    def clean_project(self):
        slug = self.cleaned_data.get("project_slug")
        if slug and not Project.objects.filter(slug=slug).exists():
            raise ValidationError("Project not found")
        return Project.objects.filter(slug=slug).last()
