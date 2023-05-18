from graphene import ID, Date, Decimal, InputObjectType, Int, String

__all__ = [
    "LandingRequestInput",
    "VacancyRequestInput",
    "SaleRequestInput",
    "NameAndPhoneInput",
    "MediaRequestInput",
    "CustomRequestInput",
    "AgentRequestInput",
    "AntiCorruptionInput",
    "LotCardRequestInput",
    "StartSaleRequestInput",
    "ContractorRequestInput",
    "PropertyAndProjectInput",
    "PurchaseHelpRequestInput",
    "NewsletterSubscriptionInput",
    "DirectorCommunicateRequestInput",
    "CallbackRequestInput",
    "PresentationRequestInput",
    "CommercialKotelnikiRequestInput",
    "BeFirstRequestInput",
    "AdvantageFormRequestInput",
]


class VacancyRequestInput(InputObjectType):
    """
    Данные отклика на вакансию
    """

    name = String(required=True)
    phone = String(required=True)
    city = String(required=True)
    position = String(required=True)

    vacancy = ID()
    category = ID()
    message = String()
    specialty = String()
    institution = String()
    graduated_at = Date()


class SaleRequestInput(InputObjectType):
    """
    Данные заявки на продажу земельного участвка
    """

    name = String(required=True)
    phone = String(required=True)
    cadastral_number = String(required=True)

    price = Decimal()
    email = String()
    message = String()


class NameAndPhoneInput(InputObjectType):
    """
    Данные телефона и имени
    """

    name = String(required=True)
    phone = String(required=True)
    project_slug = String(required=False)
    property_type = String(required=False)
    property = String(required=False)
    related_object = String(required=False)


class PropertyAndProjectInput(InputObjectType):
    """
    Данные проекта и объекта недвижимости
    """

    project_slug = String(required=False)
    property_type = String(required=False)
    property = String(required=False)


class DirectorCommunicateRequestInput(NameAndPhoneInput):
    """
    Данные для запроса на связь с директором
    """

    text = String(required=True)

    email = String()


class NewsletterSubscriptionInput(InputObjectType):
    """
    Данные для заявки на подписку
    """

    email = String(required=True)


class MediaRequestInput(InputObjectType):
    """Данные для заявки СМИ"""

    name = String(required=True)
    phone = String(required=True)
    email = String(required=True)
    comment = String(required=True)
    media_name = String(required=False)


class CustomRequestInput(NameAndPhoneInput):
    """
    Данные кастомной заявки
    """

    form = Int(required=True)
    property_id = String(required=False)


class AgentRequestInput(NameAndPhoneInput):
    city_name = String(required=True)
    agency_name = String(required=True)


class ContractorRequestInput(NameAndPhoneInput):
    type_of_job = String(required=True)
    about_company = String(required=True)


class LandingRequestInput(InputObjectType):
    """
    Данные заявки лендинга
    """

    name = String(required=True)
    email = String()
    phone = String(required=True)
    block = Int(required=True)


class AntiCorruptionInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    message = String(required=True)


class LotCardRequestInput(InputObjectType):
    phone = String(required=True)
    interval = String(required=True)
    related_object = String(required=True)


class StartSaleRequestInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    phone = String(required=True)
    project_slug = String(required=True)
    property_type = String(required=True)


class StartProjectsRequestInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    phone = String(required=True)
    project_slug = String(required=True)
    applicant = String(required=True)


class EKBStartSaleRequestInput(InputObjectType):
    name = String(required=False)
    phone = String(required=True)
    email = String(required=False)
    applicant = String(required=True)


class PurchaseHelpRequestInput(InputObjectType):
    name = String(required=True)
    phone = String(required=True)
    property_type = String(required=True)


class CallbackRequestInput(InputObjectType):
    name = String(required=True)
    phone = String(required=True)
    interval = String(required=True)
    timezone_user = String(requred=False)


class PresentationRequestInput(InputObjectType):
    phone = String(required=True)
    project_slug = String(required=True)


class CommercialKotelnikiRequestInput(InputObjectType):
    name = String(required=True)
    phone = String(required=True)
    from_url = String(required=True)


class BeFirstRequestInput(InputObjectType):
    email = String(requered=True)
    subdomain = String(required=True)


class AdvantageFormRequestInput(InputObjectType):
    phone = String(requered=True)
    project_slug = String(required=True)
