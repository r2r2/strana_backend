from typing import NewType

import tortoise
from common import amocrm, email, files, getdoc, messages, paginations, redis
from passlib import context
from src.admins import repos as admins_repos
from src.agents import repos as agents_repos
from src.agreements import repos as agreements_repos
from src.booking import repos as booking_repos
from src.getdoc import repos as getdoc_repos
from src.projects import repos as project_repos
from src.represes import repos as represes_repos
from src.represes import services as represes_services
from src.users import repos as users_repos

AgencyRedis = NewType("AgencyRedis", redis.Redis)
AgencyORM = NewType("AgencyORM", tortoise.Tortoise)
AgencyUser = NewType("AgencyUser", users_repos.User)
AgencyAmoCRM = NewType("AgencyAmoCRM", amocrm.AmoCRM)
AgencyGetDoc = NewType("AgencyGetdoc", getdoc.GetDoc)
AgencySms = NewType("AgencySms", messages.SmsService)
AgencyCheck = NewType("AgencyCheck", users_repos.Check)
AgencyEmail = NewType("AgencyEmail", email.EmailService)
AgencyHasher = NewType("AgencyHasher", context.CryptContext)
AgencyBooking = NewType("AgencyBooking", booking_repos.Booking)
AgencyUserRepo = NewType("AgencyUserRepo", users_repos.UserRepo)
AgencyCheckRepo = NewType("AgencyCheckRepo", users_repos.CheckRepo)
AgencyAgentRepo = NewType("AgencyAgentRepo", agents_repos.AgentRepo)
AgencyFileProcessor = NewType("AgencyFileProcessor", files.FileProcessor)
AgencyFileDestroyer = NewType("AgencyFileProcessor", files.FileDestroyer)
AgencyRepresRepo = NewType("AgencyRepresRepo", represes_repos.RepresRepo)
AgencyAdminsRepo = NewType("AgencyAdminsepo", admins_repos.AdminRepo)
AgencyPagination = NewType("AgencyPagination", paginations.PagePagination)
AgencyBookingRepo = NewType("AgencyBookingRepo", booking_repos.BookingRepo)
AgencyProjectRepo = NewType("AgencyProjectRepo", project_repos.ProjectRepo)
AgencyCreateContactService = NewType(
    "AgencyCreateContactService", represes_services.CreateContactService
)
AgencyAgreementRepo = NewType("AgencyAgreementRepo", agreements_repos.AgencyAgreementRepo)
AgencyAgreementTypeRepo = NewType("AgencyAgreementTypeRepo", agreements_repos.AgreementTypeRepo)
AgencyDocTemplateRepo = NewType("AgencyDocTemplateRepo", getdoc_repos.DocTemplateRepo)
AgencyActTemplateRepo = NewType("AgencyActTemplateRepo", getdoc_repos.ActTemplateRepo)
AgencyAdditionalAgreementRepo = NewType("AgencyAdditionalAgreementRepo", agreements_repos.AgencyAdditionalAgreement)
AdditionalAgreementTemplateRepo = NewType(
    "AdditionalAgreementTemplateRepo", getdoc_repos.AdditionalAgreementTemplateRepo
)
