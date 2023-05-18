from src.agents.entities import BaseAgentModel


class RequestInitializeChangePhone(BaseAgentModel):
    phone: str


class RequestInitializeChangeEmail(BaseAgentModel):
    email: str
