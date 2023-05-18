# pylint: disable=unused-argument
import agreements.models
from agencies import models as agencies_models
from amocrm import models as amocrm_models
from booking import models as booking_models
from buildings import models as buildings_models
from cautions import models as caution_models
from cities import models as cities_models
from disputes import models as disputes_models
from documents import models as documents_models
from floors import models as floors_models
from managers import models as managers_models
from pages import models as pages_models
from projects import models as projects_models
from properties import models as properties_models
from tips import models as tips_models
from users import models as users_models
from questionnaire import models as questionnaire_models
from task_management import models as task_management_models


cabinet_models: list = [
    booking_models.Booking,
    booking_models.BookingLog,
    booking_models.BookingHelpText,
    buildings_models.Building,
    documents_models.Document,
    documents_models.Escrow,
    projects_models.Project,
    properties_models.Property,
    users_models.CabinetUser,
    floors_models.Floor,
    tips_models.Tip,
    pages_models.BrokerRegistration,
    agencies_models.Agency,
    agencies_models.AgencyAct,
    agencies_models.AgencyAgreement,
    agencies_models.AgencyLog,
    agencies_models.AgencyAdditionalAgreement,
    pages_models.CheckUnique,
    pages_models.ShowtimeRegistration,
    managers_models.Manager,
    disputes_models.Dispute,
    cities_models.Cities,
    amocrm_models.AmocrmPipeline,
    amocrm_models.AmocrmStatus,
    amocrm_models.AmocrmAction,
    amocrm_models.StatusActionThrough,
    users_models.CitiesThrough,
    users_models.PipelinesThrough,
    users_models.StatusesThrough,
    users_models.CabinetChecksTerms,
    users_models.UserLog,
    users_models.UserRole,
    users_models.CheckHistory,
    users_models.UserNotificationMute,
    users_models.RealIpUsers,
    users_models.FakeUserPhone,
    caution_models.Caution,
    caution_models.CautionMute,
    agreements.models.DocTemplate,
    agreements.models.ActTemplate,
    agreements.models.AgreementStatus,
    agreements.models.AgreementType,
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
    agreements.models.AdditionalAgreementStatus,
    agreements.models.AdditionalAgreementTemplate,
    task_management_models.TaskStatus,
    task_management_models.Button,
    task_management_models.TaskInstance,
    task_management_models.TaskChain,
    task_management_models.TaskChainStatusThrough,
    task_management_models.TaskChainTaskVisibilityStatusThrough,
    amocrm_models.AmocrmGroupStatus,
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
