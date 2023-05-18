from src.getdoc.entities import BaseTemplateModel


class DocTemplateModel(BaseTemplateModel):
    """
    Модель шаблонов договоров
    """

    id: int
    project_id: int
    project_name: str
    pipline_id: int
    template_name: str

    class Config:
        orm_mode = True
