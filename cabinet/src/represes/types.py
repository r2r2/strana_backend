import tortoise
from typing import NewType
from passlib import context
from common import amocrm, email, files, messages, redis, session
from src.admins import repos as admins_repos
from src.agencies import repos as agencies_repos
from src.agents import repos as agent_repos


RepresRedis = NewType("RepresRedis", redis.Redis)
RepresORM = NewType("RepresORM", tortoise.Tortoise)
RepresAmoCRM = NewType("RepresAmoCRM", amocrm.AmoCRM)
RepresSms = NewType("RepresSms", messages.SmsService)
RepresEmail = NewType("RepresEmail", email.EmailService)
RepresHasher = NewType("RepresHasher", context.CryptContext)
RepresAgency = NewType("RepresAgency", agencies_repos.Agency)
RepresSession = NewType("RepresSession", session.SessionStorage)
RepresAdminsRepo = NewType("RepresAdminsRepo", admins_repos.AdminRepo)
RepresAgentRepo = NewType("RepresAgentRepo", agent_repos.AgentRepo)
RepresAgencyRepo = NewType("RepresAgencyRepo", agencies_repos.AgencyRepo)
RepresFileProcessor = NewType("RepresFileProcessor", files.FileProcessor)
