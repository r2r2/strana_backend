import tortoise
from typing import NewType

from passlib import context
from common import session, email, paginations, messages, redis, amocrm

from src.admins import repos as admin_repos
from src.users import repos as users_repos
from src.booking import repos as booking_repos
from src.agencies import repos as agencies_repos


AgentRedis = NewType("AgentRedis", redis.Redis)
AgentORM = NewType("AgentORM", tortoise.Tortoise)
AgentUser = NewType("AgentUser", users_repos.User)
AgentSms = NewType("AgentSms", messages.SmsService)
AgentAmoCRM = NewType("AgentAmoCRM", amocrm.AmoCRM)
AgentCheck = NewType("AgentCheck", users_repos.Check)
AgentEmail = NewType("AgentEmail", email.EmailService)
AgentHasher = NewType("AgentHasher", context.CryptContext)
AgentAgency = NewType("AgentAgency", agencies_repos.Agency)
AgentAdminRepo = NewType("AgentAdminRepo", admin_repos.AdminRepo)
AgentBooking = NewType("AgentBooking", booking_repos.Booking)
AgentSession = NewType("AgentSession", session.SessionStorage)
AgentUserRepo = NewType("AgentUserRepo", users_repos.UserRepo)
AgentCheckRepo = NewType("AgentCheckRepo", users_repos.CheckRepo)
AgentAgencyRepo = NewType("AgentAgencyRepo", agencies_repos.AgencyRepo)
AgentPagination = NewType("AgentPagination", paginations.PagePagination)
AgentBookingRepo = NewType("AgentBookingRepo", booking_repos.BookingRepo)
