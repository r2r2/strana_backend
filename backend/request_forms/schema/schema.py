from binascii import Error as BinasciiError
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils.timezone import now
from graphene_django_optimizer import query
from graphql_relay.node.node import from_global_id
from phonenumber_field.formfields import PhoneNumberField

from common.schema import ErrorType
from common.utils import collect_form_errors
from graphene import ID, Boolean, Field, List, Mutation, ObjectType, String
from projects.models import Project
from properties.models import Property

from ..forms import *
from ..forms import EKBStartSaleRequestForm, StartProjectsRequestForm
from ..models import *
from ..models import EKBStartSaleRequest, StartProjectsRequest
from ..services import RequestEmail
from .inputs import *
from .inputs import EKBStartSaleRequestInput, StartProjectsRequestInput
from .mixins import RequestMutationMixin
from .types import *
from .types import EKBStartSaleRequestType, StartProjectsRequestType


class VacancyRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация отклика на вакансию
    """

    class Arguments:
        input = VacancyRequestInput(required=True)

    request = Field(VacancyRequestType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        try:
            if input.get("vacancy"):
                vacancy_id = from_global_id(input.get("vacancy"))[1]
                input["vacancy"] = vacancy_id
            if input.get("category"):
                category_id = from_global_id(input.get("category"))[1]
                input["category"] = category_id
        except (UnicodeDecodeError, BinasciiError, ValueError) as e:
            pass

        form = VacancyRequestForm(data=input)
        if form.is_valid():
            data = form.cleaned_data
            if info.context.FILES.get("resume"):
                data.update({"resume": info.context.FILES.get("resume")})
            instance = VacancyRequest.objects.create(**data)
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance, errors=None)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class MediaRequestMutation(Mutation):
    """Мутация заявки для СМИ"""

    class Arguments:
        input = MediaRequestInput(required=True)

    ok = Boolean()
    request = Field(MediaRequestType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = MediaRequestForm(data=input)
        if form.is_valid():
            instance = form.save()
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance, errors=None)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class SaleRequestMutation(Mutation):
    """
    Мутация запроса на продажу земельного участка
    """

    class Arguments:
        input = SaleRequestInput(required=True)

    ok = Boolean()
    request = Field(SaleRequestType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = SaleRequestForm(data=input)
        if form.is_valid():
            instance = form.save()
            for file in info.context.FILES.getlist("documents"):
                SaleRequestDocument.objects.create(request=instance, file=file)
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class DirectorCommunicateRequestMutation(Mutation):
    """
    Мутация запрсо на связь с директором
    """

    class Arguments:
        input = DirectorCommunicateRequestInput(required=True)

    ok = Boolean()
    request = Field(DirectorCommunicateRequestType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = DirectorCommunicateRequestForm(data=input)
        if form.is_valid():
            slug = form.cleaned_data.get("project_slug")
            project = Project.objects.get(slug=slug) if slug else None
            property_type = form.cleaned_data.get("property_type") or ""

            instance = DirectorCommunicateRequest.objects.create(
                name=form.cleaned_data.get("name"),
                phone=form.cleaned_data.get("phone"),
                email=form.cleaned_data.get("email"),
                text=form.cleaned_data.get("text"),
                project=project,
                property_type=property_type,
            )
            RequestEmail(instance, info.context)()

            # отключил отправку в СРМ
            # instance.send_amocrm_lead(info.context)
            return cls(ok=True, request=instance)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class NewsletterSubscriptionMutation(Mutation):
    """
    Мутация заявки на подписку
    """

    class Arguments:
        input = NewsletterSubscriptionInput(required=True)

    ok = Boolean()
    request = Field(NewsletterSubscriptionType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = NewsletterSubscriptionForm(data=input)
        if form.is_valid():
            instance, _ = NewsletterSubscription.objects.get_or_create(
                email=form.cleaned_data.get("email")
            )
            return cls(ok=True, request=instance)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class ValidatePhoneMutation(Mutation):
    """
    Мутация подтверждения телефона
    """

    class Arguments:
        phone = String(required=True)

    ok = Boolean()
    phone = String()

    @classmethod
    def mutate(cls, obj, info, phone=None):
        field = PhoneNumberField()
        try:
            phone = field.clean(phone)
        except ValidationError as e:
            return cls(ok=False)

        return cls(ok=True, phone=phone)


class CustomRequestMutation(Mutation):
    """
    Мутация кастомной заявки
    """

    class Arguments:
        input = CustomRequestInput(required=True)

    ok = Boolean()
    request = Field(CustomRequestType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = CustomRequestForm(data=input)
        if form.is_valid():
            slug = form.cleaned_data.get("project_slug")
            project = Project.objects.get(slug=slug) if slug else None
            property_type = form.cleaned_data.get("property_type") or ""
            form_id = form.cleaned_data.get("form")
            form_instance = CustomForm.objects.get(id=form_id)
            property_id = form.cleaned_data.get("property_id")
            property = Property.objects.get(id=property_id) if property_id else None

            instance = CustomRequest.objects.create(
                form=form_instance,
                property=property,
                name=form.cleaned_data.get("name"),
                phone=form.cleaned_data.get("phone"),
                project=project,
                property_type=property_type,
            )
            RequestEmail(instance, info.context)()
            instance.send_amocrm_lead(info.context)
            return cls(ok=True, request=instance)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class PurchaseHelpRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на помощь с покупкой
    """

    request_model = PurchaseHelpRequest
    request = Field(PurchaseHelpRequestType)

    class Arguments:
        input = PurchaseHelpRequestInput(required=True)


class CommercialRentRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на аренду коммерческих помещений
    """

    request_model = CommercialRentRequest
    request = Field(CommercialRentRequestType)


class CallbackRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на обратную связь
    """

    form = CallbackRequestForm
    request_model = CallbackRequest
    request = Field(CallbackRequestType)
    send_to_amocrm = False

    class Arguments:
        input = CallbackRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = cls.form(data=input)
        if form.is_valid():
            if settings.DEBUG:
                qs = cls.request_model.objects.filter(
                    phone=form.cleaned_data.get("phone"), date__gt=now() - timedelta(seconds=5)
                )
                if qs.exists():
                    return cls(ok=True, request=qs.first())

            slug = form.cleaned_data.get("project_slug")
            project = Project.objects.get(slug=slug) if slug else None
            property_type = form.cleaned_data.get("property_type") or ""
            property_id = form.cleaned_data.get("property") or None
            related_object = form.cleaned_data.get("related_object") or None
            interval = form.cleaned_data.get("interval")

            data = {
                "name": form.cleaned_data.get("name", ""),
                "phone": form.cleaned_data.get("phone"),
                "amo_send": False,
                "site": info.context.site,
                "cookies": info.context.COOKIES,
                "referer": info.context.headers.get("referer"),
            }
            if project:
                data.update({"project": project})
            if property_type:
                data.update({"property_type": property_type})
            if property_id:
                data.update({"property_id": property_id})
            if related_object:
                data.update({"related_object": related_object})
            if interval:
                data.update({"interval": interval})
            data.update()

            instance = cls.request_model.objects.create(**data)
            RequestEmail(instance, info.context)()
            if instance.in_interval():
                instance.send_amocrm_lead_without_http()
            return cls(ok=True, request=instance)
        else:
            return cls(ok=False, request=None, errors=collect_form_errors(form))


class TeaserRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация запроса со слайда главной страницы
    """

    request_model = TeaserRequest
    request = Field(TeaserRequestType)
    form = TeaserRequestForm


class NewsRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация запроса со страницы новости
    """

    request_model = NewsRequest
    request = Field(NewsRequestType)
    form = NewsRequestForm


class OfficeRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на встречу в офисе
    """

    request_model = OfficeRequest
    request = Field(OfficeRequestType)
    form = OfficeRequestForm


class FlatListingRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки в листинге квартир
    """

    request_model = FlatListingRequest
    request = Field(FlatListingRequestType)


class LotCardRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки с карточки лота
    """

    request_model = LotCardRequest
    request = Field(LotCardRequestType)
    form = LotCardRequestForm

    class Arguments:
        input = LotCardRequestInput(required=True)


class ReservationRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на бронирование
    """

    request_model = ReservationRequest
    request = Field(ReservationRequestType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = NamePhoneAndProjectForm(data=input)
        if form.is_valid():

            slug = form.cleaned_data.get("project_slug")
            project = Project.objects.get(slug=slug) if slug else None
            property_type = form.cleaned_data.get("property_type") or ""

            data = {
                "name": form.cleaned_data.get("name"),
                "phone": form.cleaned_data.get("phone"),
                "project": project,
                "property_type": property_type,
            }

            property = form.cleaned_data.get("property") or None
            if property:
                data["property_id"] = property

            booking_type = form.cleaned_data.get("property") or None
            if booking_type:
                data["booking_type_id"] = booking_type

            instance = cls.request_model.objects.create(**data)
            RequestEmail(instance, info.context)()
            instance.send_amocrm_lead(info.context)
            return cls(ok=True, request=instance)
        else:
            return cls(ok=False, request=None, errors=collect_form_errors(form))


class ReservationLKRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на бронирование
    """

    request_model = ReservationLKRequest
    request = Field(ReservationLKRequestType)
    lk_data = Field(LKDataType)

    class Arguments:
        input = PropertyAndProjectInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = PropertyAndProjectForm(data=input)
        if form.is_valid():
            if settings.DEBUG:
                qs = cls.request_model.objects.filter(date__gt=now() - timedelta(seconds=5))
                if qs.exists():
                    ok, lk_data = qs.first().send_lk_lead()
                    return cls(ok=ok, request=qs.first(), lk_data=lk_data)

            slug = form.cleaned_data.get("project_slug")
            property = form.cleaned_data.get("property")
            property_type = form.cleaned_data.get("property_type")
            project = Project.objects.get(slug=slug)

            data = {"project": project, "property_id": property, "property_type": property_type}

            instance = cls.request_model.objects.create(**data)
            ok, lk_data = instance.send_lk_lead()
            return cls(ok=ok, lk_data=lk_data, request=instance)
        else:
            return cls(ok=False, request=None, errors=collect_form_errors(form))


class ExcursionRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на экскурсию
    """

    request_model = ExcursionRequest
    request = Field(ExcursionRequestType)


class MallTeamRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки с блока MallTeam
    """

    request_model = MallTeamRequest
    request = Field(MallTeamRequestType)
    send_to_amocrm = False


class AgentRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки агентств
    """

    request_model = AgentRequest
    form = AgentRequestForm
    request = Field(AgentRequestType)

    class Arguments:
        input = AgentRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = AgentRequestForm(data=input)
        if form.is_valid():
            instance = AgentRequest.objects.create(**form.cleaned_data)
            RequestEmail(instance, info.context)()
            instance.send_amocrm_lead(info.context)
            return cls(ok=True, request=instance, errors=None)
        return cls(ok=False, request=None, errors=collect_form_errors(form))


class ContractorRequestMutation(Mutation):
    """
    Мутация заявки для подрячиков
    """

    ok = Boolean()
    request = Field(ContractorRequestType)
    errors = List(ErrorType)

    class Arguments:
        input = ContractorRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = ContractorRequestForm(data=input)
        if form.is_valid() and info.context.FILES.get("offer"):
            instance = ContractorRequest.objects.create(
                offer=info.context.FILES.get("offer"), **form.cleaned_data
            )
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance, errors=None)

        form_errors = collect_form_errors(form)
        if not info.context.FILES.get("offer"):
            form_errors.append({"field": "offer", "messages": ["Необходимо прикрепить файл"]})

        return cls(ok=False, request=None, errors=form_errors)


class LandingRequestMutation(Mutation):
    """
    Мутация заявки лендинга
    """

    class Arguments:
        input = LandingRequestInput(required=True)

    ok = Boolean()
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = LandingRequestForm(data=input)
        if form.is_valid():
            instance = form.save()
            instance.send_presentation()
            return cls(ok=True, errors=None)

        return cls(ok=False, errors=collect_form_errors(form))


class AntiCorruptionRequestMutation(Mutation):
    """Мутация заявки о противодействии коррупции"""

    class Arguments:
        input = AntiCorruptionInput(required=True)

    ok = Boolean()
    request = Field(AntiCorruptionRequestType)
    errors = List(ErrorType)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = AntiCorruptionForm(data=input)
        if form.is_valid():
            instance = form.save()
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance, errors=None)

        return cls(ok=False, request=None, errors=collect_form_errors(form))


class StartSaleRequestMutation(RequestMutationMixin, Mutation):
    """
    Мутация заявки на уведомление о начале старта продаж
    """

    form = StartSaleRequestForm
    request_model = StartSaleRequest
    request = Field(StartSaleRequestType)

    class Arguments:
        input = StartSaleRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = cls.form(data=input)
        if form.is_valid():

            data = form.cleaned_data
            data.update({"project": Project.objects.get(slug=data.pop("project_slug"))})

            instance = cls.request_model.objects.create(**data)
            RequestEmail(instance, info.context)()
            return cls(ok=True, request=instance)
        else:
            return cls(ok=False, request=None, errors=collect_form_errors(form))


class EKBStartSaleRequestMutation(RequestMutationMixin, Mutation):
    form = EKBStartSaleRequestForm
    request = Field(EKBStartSaleRequestType)
    request_model = EKBStartSaleRequest

    class Arguments:
        input = EKBStartSaleRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = cls.form(data=input)
        if not form.is_valid():
            return cls(ok=False, request=None, errors=collect_form_errors(form))
        html_template = "request_forms/email.html"
        subject = "Заявка на уведомление о старте продаж в Екатеринбурге"
        emails = (
            "anastasiya.utkina@strana.com",
        )
        instance, created = EKBStartSaleRequest.objects.get_or_create(**form.cleaned_data)
        send_mail(
            subject=subject, message=subject,
            from_email=settings.SERVER_EMAIL, recipient_list=emails,
            html_message=render_to_string(html_template, {"request": instance})
        )
        return cls(ok=True, request=instance)


class StartProjectsRequestMutation(RequestMutationMixin, Mutation):
    form = StartProjectsRequestForm
    request = Field(StartProjectsRequestType)
    request_model = StartProjectsRequest

    class Arguments:
        input = StartProjectsRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = cls.form(data=input)
        if not form.is_valid():
            return cls(ok=False, request=None, errors=collect_form_errors(form))

        data = form.cleaned_data
        data.update({"project": Project.objects.get(slug=data.pop("project_slug"))})
        instance = cls.request_model.objects.create(**data)
        return cls(ok=True, request=instance)


class PresentationRequestMutation(RequestMutationMixin, Mutation):

    form = PresentationRequestForm
    request = Field(PresentationRequestType)
    request_model = PresentationRequest

    class Arguments:
        input = PresentationRequestInput(required=True)


class CommercialKotelnikiRequestMutation(RequestMutationMixin, Mutation):

    form = CommercialKotelnikiRequestForm
    request = Field(CommercialKotelnikiRequestType)
    request_model = CommercialKotelnikiRequest
    send_to_amocrm = False

    class Arguments:
        input = CommercialKotelnikiRequestInput(required=True)


class BeFirstRequestMutation(Mutation):
    """Мутация заявки 'Узнайте о новых проектах'"""

    ok = Boolean()
    request = Field(BeFirstRequestType)
    errors = List(ErrorType)

    class Arguments:
        input = BeFirstRequestInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = BeFirstRequestModelForm(data=input)
        if form.is_valid():
            instance = form.save()
            return cls(ok=True, request=instance, errors=None)
        return cls(ok=False, request=None, errors=collect_form_errors(form))


class AdvantageFormRequestMutation(RequestMutationMixin, Mutation):
    """Мутация заявки с формы УТП"""

    form = AdvantageFormRequestModelForm
    request = Field(AdvantageFormRequestType)
    request_model = AdvantageFormRequest
    send_to_amocrm = True

    class Arguments:
        input = AdvantageFormRequestInput(required=True)


class ShowRequestMutation(RequestMutationMixin, Mutation):
    """Мутация заявки записи на показ"""

    request = Field(ShowRequestType)
    request_model = ShowRequest


class RequestMutation(ObjectType):
    """Мутации запросов"""

    sale_request = SaleRequestMutation.Field(description="Форма заявки на продажу участка")
    vacancy_request = VacancyRequestMutation.Field(description="Форма отклика на вакансию")
    callback_request = CallbackRequestMutation.Field(description="Форма заявки на обратный звонок")
    validate_phone = ValidatePhoneMutation.Field(description="Валидации номера телефона")
    custom_request = CustomRequestMutation.Field(description="Форма для кастомных заявок")
    agent_request = AgentRequestMutation.Field(description="Форма записи для агентов")
    contractor_request = ContractorRequestMutation.Field(description="Форма записи для подрядчиков")
    media_request = MediaRequestMutation.Field(description="Форма для СМИ")
    reservation_request = ReservationRequestMutation.Field(
        description="Форма заявки на бронирование"
    )
    reservation_lk_request = ReservationLKRequestMutation.Field(
        description="Форма заявки на бронирование в ЛК"
    )
    excursion_request = ExcursionRequestMutation.Field(description="Форма записи на экскурсию")
    director_communicate_request = DirectorCommunicateRequestMutation.Field(
        description="Форма запроса на связь с директором"
    )
    newsletter_subscription = NewsletterSubscriptionMutation.Field(
        description="Форма подписки на рассылку"
    )
    purchase_help_request = PurchaseHelpRequestMutation.Field(
        description="Форма заявки на помощь с оформлением покупки"
    )
    commercial_rent_request = CommercialRentRequestMutation.Field(
        description="Форма заявки на аренду коммерческой недвижимости"
    )
    landing_request = LandingRequestMutation.Field(description="Мутация на отправку презентации")
    anti_corruption_request = AntiCorruptionRequestMutation.Field(
        description="Форма заявки о противодействии коррупции"
    )
    teaser_request = TeaserRequestMutation.Field(
        description="Форма заявки со слайда главной страницы"
    )
    news_request = NewsRequestMutation.Field(description="Форма заявки со страницы новости")
    office_request = OfficeRequestMutation.Field(description="Форма заявки записи на встречу")
    lot_card_request = LotCardRequestMutation.Field(description="Форма заявки с карточки лота")
    flat_listing_request = FlatListingRequestMutation.Field(description="Заявка в листинге квартир")
    start_sale_request = StartSaleRequestMutation.Field(
        description="Заявка на уведомление о старте продаж"
    )
    start_project_request = StartProjectsRequestMutation.Field(
        description="Отклик старт проекта"
    )
    ekb_start_sale_request = EKBStartSaleRequestMutation.Field(
        description="Заявка на уведомление о старте продаж в Екатеринбурге"
    )
    presentation_request = PresentationRequestMutation.Field(
        description="Форма заявки на получение презентации"
    )
    mall_team_request = MallTeamRequestMutation.Field(description="Заявка с блока MallTeam")
    commercial_kotelniki_request = CommercialKotelnikiRequestMutation.Field(
        description="Заявка коммерция Котельники"
    )
    be_first_request = BeFirstRequestMutation.Field(description="Заявка 'Узнайте о новых проектах'")
    advantage_form_request = AdvantageFormRequestMutation.Field(description="Заявка с формы УТП")
    show_request = ShowRequestMutation.Field(description="Заявка записи на показ")


class RequestQuery(ObjectType):
    """Запросы запросов"""

    all_custom_forms = List(CustomFormType, description="Список кастомных форм")
    all_custom_form_employee = List(CustomFormEmployeeType, city_id=ID(), project_slug=String())
    all_flat_listing_request_forms = List(
        FlatListingRequestFormType, description="Список форм в листинге квартир"
    )

    @staticmethod
    def resolve_all_custom_forms(obj, info, **kwargs):
        return CustomForm.objects.filter(active=True)

    @staticmethod
    def resolve_all_custom_form_employee(obj, info, **kwargs):
        qs = CustomFormEmployee.objects.all()
        if kwargs.get("project_slug"):
            return query(qs.filter(project__slug=kwargs.get("project_slug")), info)
        if kwargs.get("city_id"):
            try:
                _, city_id = from_global_id(kwargs.get("city_id"))
                return query(qs.filter(project__city=city_id), info)
            except (UnicodeDecodeError, BinasciiError, ValueError):
                return None
        return query(qs, info)

    @staticmethod
    def resolve_all_flat_listing_request_forms(obj, info, **kwargs):
        return FlatListingRequestForm.objects.all()
