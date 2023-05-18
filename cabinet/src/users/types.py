import tortoise
from typing import NewType
from passlib import context
from tortoise import queryset

from src.agents import repos as agents_repos
from src.booking import repos as booking_repos
from src.projects import repos as projects_repos
from src.agencies import repos as agencies_repos
from src.properties import repos as properties_repos
from src.notifications import repos as notifications_repos
from src.users import repos as users_repos
from common import session, messages, email, amocrm, paginations

UserORM = NewType("UserORM", tortoise.Tortoise)
UserAmoCRM = NewType("UserAmoCRM", amocrm.AmoCRM)
UserSms = NewType("UserSms", messages.SmsService)
UserEmail = NewType("UserEmail", email.EmailService)
UserHasher = NewType("UserHasher", context.CryptContext)
UserAgency = NewType("UserAgency", agencies_repos.Agency)
UserBooking = NewType("UserBooking", booking_repos.Booking)
UserProject = NewType("UserProject", projects_repos.Project)
UserSession = NewType("UserSession", session.SessionStorage)
UserAgentRepo = NewType("UserAgentRepo", agents_repos.AgentRepo)
UserProperty = NewType("UserProperty", properties_repos.Property)
UserAgencyRepo = NewType("UserAgencyRepo", agencies_repos.AgencyRepo)
UserPagination = NewType("UserPagination", paginations.PagePagination)
UserBookingRepo = NewType("UserBookingRepo", booking_repos.BookingRepo)
UserProjectRepo = NewType("UserProjectRepo", projects_repos.ProjectRepo)
UserPropertyQuerySet = NewType("UserPropertyQuerySet", queryset.QuerySet)
UserPropertyRepo = NewType("UserPropertyRepo", properties_repos.PropertyRepo)
UserNotificationRepo = NewType("UserNotificationRepo", notifications_repos.NotificationRepo)
UserInterestedRepo = NewType("UserInterestedRepo", users_repos.InterestsRepo)
UserRepo = NewType("UserRepo", users_repos.UserRepo)
