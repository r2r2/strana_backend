from pydantic import BaseModel
from .agents_users_check_dispute import ResponseAgentUsersCheckDisputeModel as _ResponseAgentUsersCheckDisputeModel
from ..constants import ResolveDisputeStatuses


class RequestAdminsUserCheckDispute(BaseModel):
    status: ResolveDisputeStatuses


class ResponseAdminsUserCheckDispute(_ResponseAgentUsersCheckDisputeModel):
    pass
