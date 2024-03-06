from typing import Any, Literal, NamedTuple, NewType, Optional, TypedDict

import tortoise
from common import (amocrm, email, files, messages, profitbase, requests,
                    sberbank, session)
from src.agents import repos as agents_repos
from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from src.notifications import repos as notifications_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.users import repos as users_repos
from tortoise import queryset

BookingORM = NewType("BookingORM", tortoise.Tortoise)
BookingUser = NewType("BookingUser", users_repos.User)
BookingSms = NewType("BookingSms", messages.SmsService)
BookingAmoCRM = NewType("BookingAmoCRM", amocrm.AmoCRM)
BookingAgent = NewType("BookingAgent", agents_repos.User)
BookingEmail = NewType("BookingEmail", email.EmailService)
BookingFloor = NewType("BookingFloor", floors_repos.Floor)
BookingSberbank = NewType("BookingSberbank", sberbank.Sberbank)
BookingQuerySet = NewType("BookingQuerySet", queryset.QuerySet)
BookingRequest = NewType("BookingRequest", requests.CommonRequest)
BookingUserRepo = NewType("BookingUserRepo", users_repos.UserRepo)
BookingProject = NewType("BookingProject", projects_repos.Project)
BookingSession = NewType("BookingSession", session.SessionStorage)
BookingAgentRepo = NewType("BookingAgentRepo", agents_repos.AgentRepo)
BookingBuilding = NewType("BookingBuilding", buildings_repos.Building)
BookingFloorRepo = NewType("BookingFloorRepo", floors_repos.FloorRepo)
BookingProperty = NewType("BookingProperty", properties_repos.Property)
BookingProfitBase = NewType("BookingProfitBase", profitbase.ProfitBase)
BookingFileProcessor = NewType("BookingFileProcessor", files.FileProcessor)
BookingFileClient = NewType("BookingFileClient", files.FileClient)
BookingFileValidator = NewType("BookingFileValidator", files.UploadedFileValidation)
BookingProjectRepo = NewType("BookingProjectRepo", projects_repos.ProjectRepo)
BookingGraphQLRequest = NewType("BookingGraphQLRequest", requests.GraphQLRequest)
BookingBuildingRepo = NewType("BookingBuildingRepo", buildings_repos.BuildingRepo)
BookingPropertyRepo = NewType("BookingPropertyRepo", properties_repos.PropertyRepo)
BookingSqlUpdateRequest = NewType("BookingSqlUpdateRequest", requests.UpdateSqlRequest)
BookingNotificationRepo = NewType("BookingNotificationRepo", notifications_repos.NotificationRepo)


class ScannedPassportData(TypedDict):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    gender: Optional[Literal["male", "female"]]


class BookingTypeNamedTuple(NamedTuple):
    price: int
    period: int


class CustomFieldValue(NamedTuple):
    name: Optional[str] = None
    value: Optional[Any] = None
    enum: Optional[int] = None


class WebhookLead(NamedTuple):
    lead_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    new_status_id: Optional[int] = None
    custom_fields: dict[int, CustomFieldValue] = {}
    tags: dict[int, str] = {}
    updated_at: int | None = None


class WebhookContact(NamedTuple):
    amocrm_id: int
    fullname: str
    custom_fields: dict[int, CustomFieldValue] = {}
    tags: dict[int, str] = {}
    role: Optional[str] = None
