from ..entities import BaseNotificationModel
from ..repos.client_notification import ClientNotificationSchema


class ResponseClientNotificationsModel(BaseNotificationModel):
    next_page: bool
    results: list[ClientNotificationSchema]


class IsNewModel(BaseNotificationModel):
    label: str
    value: bool
    exists: bool


class ResponseClientNotificationsSpecsModel(BaseNotificationModel):
    is_new: list[IsNewModel]
