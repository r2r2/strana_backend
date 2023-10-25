from pydantic import BaseModel, constr, Field


class DepregParticipantDTO(BaseModel):
    """
    Модель ответа DepregAPI [GET] /participants
    """
    id: int | None
    event_id: int | None = Field(alias="eventId")
    group_id: int | None = Field(alias="groupId")
    code: constr(max_length=255) | None
    name: str | None
    surname: str | None
    patronymic: str | None
    email: str | None
    phone: str | None
    company: str | None
    info: dict[str, str] | None
    marked: bool | None

    class Config:
        orm_mode = True


class DepregParticipantsDTO(BaseModel):
    """
    Модель ответа DepregAPI [GET] /participants
    """
    data: list[DepregParticipantDTO]


class DepregGroupDTO(BaseModel):
    """
    Модель ответа DepregAPI [GET] /groups/{id}
    """
    id: int
    event_id: int = Field(alias="eventId")
    template_id: int | None = Field(alias="templateId")
    created_at: str | None = Field(alias="createdAt")
    timeslot: str | None = Field(alias="name")

    class Config:
        orm_mode = True
