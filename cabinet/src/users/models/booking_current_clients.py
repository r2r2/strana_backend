from pydantic import BaseModel, Field, validator, constr, EmailStr


class RequestBookingCurrentClient(BaseModel):
    user_id: int
    active_project: int = Field(description='Активный ЖК(проект)')
