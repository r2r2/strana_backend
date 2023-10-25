# pylint: disable=unused-argument
from artefacts import models as artefacts_models
from booking import models as booking_models
from contents import models as contents_models
from dashboard import models as dashboard_models
from disputes import models as disputes_models
from documents import models as documents_models
from events import models as event_models
from main_page import models as main_page_models
from managers import models as managers_models
from notifications import models as notifications_models
from properties import models as properties_models
from questionnaire import models as questionnaire_models
from references import models as references_models
from task_management import models as task_management_models
from users import models as users_models
from amocrm import models as amocrm_models
from additional_services import models as add_services_models
from events_list import models as events_list_models

from settings import models as settings_models

cabinet_models: list = [
    booking_models.Booking,
    booking_models.BookingLog,
    booking_models.BookingTag,
    booking_models.AmocrmPipeline,
    booking_models.AmocrmStatus,
    booking_models.AmocrmAction,
    booking_models.AmocrmGroupStatus,
    booking_models.GroupStatusActionThrough,
    booking_models.ClientAmocrmGroupStatus,
    booking_models.BookingFixingConditionsMatrix,
    booking_models.BookingFixingConditionsMatrixProjects,
    booking_models.BookingFixingConditionsMatrixPipelineThrough,
    booking_models.BookingReservationMatrix,
    booking_models.BookingReservationMatrixProjects,
    booking_models.GroupStatusTagThrough,
    booking_models.ClientGroupStatusTagThrough,
    booking_models.PaymentMethod,
    booking_models.PriceOfferMatrix,
    booking_models.BookingSource,
    booking_models.AdditionalServiceGroupStatus,
    booking_models.PriceImportMatrixCitiesThrough,
    booking_models.PriceImportMatrix,
    booking_models.PriceSchema,
    properties_models.Property,
    properties_models.Building,
    properties_models.BuildingBookingTypeThrough,
    properties_models.BuildingBookingType,
    properties_models.Section,
    properties_models.Project,
    properties_models.Floor,
    properties_models.PropertyType,
    properties_models.PropertyTypePipelineThrough,
    properties_models.PropertyPrice,
    properties_models.PropertyPriceType,
    properties_models.MortgageType,
    users_models.CabinetUser,
    users_models.CabinetAgent,
    users_models.CabinetAdmin,
    users_models.CabinetClient,
    documents_models.AgencyAct,
    documents_models.AgencyAgreement,
    documents_models.AgencyAdditionalAgreement,
    documents_models.DocTemplate,
    documents_models.ActTemplate,
    documents_models.AgreementStatus,
    documents_models.AgreementType,
    documents_models.AdditionalAgreementStatus,
    documents_models.AdditionalAgreementTemplate,
    documents_models.AgencyAdditionalAgreementCreatingData,
    documents_models.AdditionalProjectThrough,
    documents_models.AdditionalAgencyThrough,
    artefacts_models.CheckUnique,
    artefacts_models.ShowtimeRegistration,
    artefacts_models.Document,
    artefacts_models.Escrow,
    artefacts_models.BookingHelpText,
    artefacts_models.Tip,
    managers_models.Manager,
    disputes_models.ConfirmClientAssign,
    disputes_models.Dispute,
    disputes_models.CheckHistory,
    disputes_models.AmoCrmCheckLog,
    disputes_models.ConsultationType,
    disputes_models.PinningStatus,
    disputes_models.PinningStatusCity,
    disputes_models.PinningStatusPipeline,
    disputes_models.PinningStatusStatus,
    disputes_models.UniqueStatus,
    disputes_models.CabinetChecksTerms,
    disputes_models.CitiesThrough,
    disputes_models.PipelinesThrough,
    disputes_models.StatusesThrough,
    disputes_models.UniqueStatusButton,
    disputes_models.DisputeStatus,
    # disputes_models.UsersCheck,
    references_models.Acquiring,
    references_models.Cities,
    references_models.CityMenuThrough,
    references_models.RoleMenuThrough,
    references_models.Menu,
    references_models.PaymentPageNotification,
    users_models.UserLog,
    users_models.UserRole,
    users_models.UserNotificationMute,
    users_models.RealIpUsers,
    users_models.FakeUserPhone,
    users_models.Agency,
    users_models.AgencyGeneralType,
    users_models.AgencyLog,
    users_models.HistoricalDisputeData,
    users_models.CityUserThrough,
    contents_models.Caution,
    contents_models.CautionMute,
    contents_models.TextBlock,
    contents_models.BrokerRegistration,
    contents_models.Instruction,
    questionnaire_models.FunctionalBlock,
    questionnaire_models.QuestionGroup,
    questionnaire_models.Question,
    questionnaire_models.Answer,
    questionnaire_models.Matrix,
    questionnaire_models.MatrixConditionsThrough,
    questionnaire_models.Condition,
    questionnaire_models.QuestionnaireDocumentBlock,
    questionnaire_models.QuestionnaireDocument,
    questionnaire_models.QuestionnaireUploadDocument,
    questionnaire_models.UserAnswer,
    questionnaire_models.TaskInstanceLog,
    task_management_models.TaskStatus,
    task_management_models.Button,
    task_management_models.TaskInstance,
    task_management_models.TaskChain,
    task_management_models.TaskChainStatusThrough,
    task_management_models.TaskChainTaskVisibilityStatusThrough,
    task_management_models.TaskField,
    task_management_models.TaskChainTaskFieldsThrough,
    task_management_models.TaskStatusButtonsThrough,
    task_management_models.TaskChainBookingSourceThrough,
    task_management_models.ButtonDetailView,
    task_management_models.TaskStatusButtonsDetailThrough,
    notifications_models.LogEmail,
    notifications_models.LogSms,
    notifications_models.EmailTemplate,
    notifications_models.SmsTemplate,
    notifications_models.AssignClientTemplate,
    notifications_models.BookingNotification,
    notifications_models.BookingNotificationsProjectThrough,
    notifications_models.BookingFixationNotification,
    notifications_models.BookingFixationNotificationsProjectThrough,
    notifications_models.EventsSmsNotification,
    notifications_models.EventsSmsNotificationCityThrough,
    notifications_models.EmailHeaderTemplate,
    notifications_models.EmailFooterTemplate,
    notifications_models.QRcodeSMSNotify,
    notifications_models.QRcodeSMSCityThrough,
    notifications_models.QRcodeSMSEventListThrough,
    event_models.Event,
    event_models.CalendarEvent,
    event_models.CalendarEventTypeSettings,
    event_models.MeetingStatus,
    event_models.CalendarEventTagThrough,
    event_models.EventTag,
    event_models.EventParticipant,
    event_models.Meeting,
    event_models.MeetingCreationSource,
    events_list_models.EventList,
    events_list_models.EventParticipantList,
    dashboard_models.Ticket,
    dashboard_models.TicketCityThrough,
    dashboard_models.Block,
    dashboard_models.BlockCityThrough,
    dashboard_models.Element,
    dashboard_models.ElementCityThrough,
    dashboard_models.Link,
    dashboard_models.LinkCityThrough,
    settings_models.BookingSettings,
    settings_models.AddServiceSettings,
    settings_models.DaDataSettings,
    main_page_models.MainPageContent,
    main_page_models.MainPageOffer,
    main_page_models.MainPagePartnerLogo,
    main_page_models.MainPageSellOnline,
    main_page_models.MainPageManager,
    amocrm_models.AmoCRMSettings,
    add_services_models.AdditionalServiceCategory,
    add_services_models.AdditionalServiceCondition,
    add_services_models.AdditionalService,
    add_services_models.AdditionalServiceConditionStep,
    add_services_models.AdditionalServiceTicket,
    add_services_models.AdditionalServiceType,
    add_services_models.AdditionalServiceTemplate,
]


class DatabaseRouter:
    """
    Router for cabinet database
    """

    def db_for_read(self, model, **hints) -> str:
        database: str = "default"
        if model in cabinet_models:
            database: str = "lk"
        return database

    def db_for_write(self, model, **hints) -> str:
        database: str = "default"
        if model in cabinet_models:
            database: str = "lk"
        return database
