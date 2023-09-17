from pydantic import BaseModel, EmailStr, Field, constr, validator


class RequestBookingCurrentClient(BaseModel):
    user_id: int = Field(alias="userId")
    active_project: int = Field(description='Активный ЖК(проект)', alias="activeProject")
