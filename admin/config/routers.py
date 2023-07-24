# pylint: disable=unused-argument
from documents import models as documents_models
from booking import models as booking_models
from contents import models as contents_models
from references import models as references_models
from disputes import models as disputes_models
from managers import models as managers_models
from artefacts import models as artefacts_models
from properties import models as properties_models
from users import models as users_models
from questionnaire import models as questionnaire_models
from task_management import models as task_management_models
from notifications import models as notifications_models
from meetings import models as meetings_models
from events import models as event_models
from dashboard import models as dashboard_models
from settings import models as settings_models


cabinet_models: list = [
    booking_models.Booking,
    booking_models.BookingLog,
    booking_models.AmocrmPipeline,
    booking_models.AmocrmStatus,
    booking_models.AmocrmAction,
    booking_models.AmocrmGroupStatus,
    booking_models.GroupStatusActionThrough,
    properties_models.Property,
    properties_models.Building,
    properties_models.Project,
    properties_models.Floor,
    users_models.CabinetUser,
    users_models.CabinetAgent,
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
    disputes_models.PinningStatus,
    disputes_models.PinningStatusCity,
    disputes_models.PinningStatusPipeline,
    disputes_models.PinningStatusStatus,
    disputes_models.UniqueStatus,
    disputes_models.CabinetChecksTerms,
    disputes_models.CitiesThrough,
    disputes_models.PipelinesThrough,
    disputes_models.StatusesThrough,
    references_models.Cities,
    references_models.Menu,
    users_models.UserLog,
    users_models.UserRole,
    users_models.CityUserThrough,
    users_models.UserNotificationMute,
    users_models.RealIpUsers,
    users_models.FakeUserPhone,
    users_models.Agency,
    users_models.AgencyLog,
    users_models.HistoricalDisputeData,
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
    notifications_models.LogEmail,
    notifications_models.LogSms,
    notifications_models.EmailTemplate,
    notifications_models.SmsTemplate,
    notifications_models.AssignClientTemplate,
    meetings_models.Meeting,
    event_models.Event,
    event_models.EventTag,
    event_models.EventParticipant,
    event_models.EventTagThrough,
    dashboard_models.Ticket,
    dashboard_models.TicketCityThrough,
    dashboard_models.Block,
    dashboard_models.BlockCityThrough,
    dashboard_models.Element,
    dashboard_models.ElementCityThrough,
    dashboard_models.Link,
    dashboard_models.LinkCityThrough,
    settings_models.BookingSettings,
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
