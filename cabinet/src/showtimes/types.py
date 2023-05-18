import tortoise
from typing import NewType
from common import email, amocrm
from src.users import repos as users_repos
from src.agents import repos as agents_repos
from src.projects import repos as projects_repos


ShowTimeORM = NewType("ShowTImeORM", tortoise.Tortoise)
ShowTimeUser = NewType("ShowTimeUser", users_repos.User)
ShowTimeAmoCRM = NewType("ShowTimeAmoCRM", amocrm.AmoCRM)
ShowTimeEmail = NewType("ShowTimeEmail", email.EmailService)
ShowTimeProject = NewType("ShowTimeProject", projects_repos.Project)
ShowTimeUserRepo = NewType("ShowTimeUserRepo", users_repos.UserRepo)
ShowTimeAgentRepo = NewType("ShowTimeAgentRepo", agents_repos.AgentRepo)
ShowTimeProjectRepo = NewType("ShowTimeProjectRepo", projects_repos.ProjectRepo)
