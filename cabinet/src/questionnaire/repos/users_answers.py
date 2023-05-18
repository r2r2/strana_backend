from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class UserAnswer(BaseQuestionnaireModel):
    """
    Ответ пользователя
    """
    id: int = fields.IntField(description='ID', pk=True)
    user: fields.ForeignKeyNullableRelation['User'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Пользователь",
        model_name="models.User",
        related_name="answered_user",
        null=True,
    )
    question_group: fields.ForeignKeyNullableRelation['QuestionGroup'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Группа вопроса",
        model_name="models.QuestionGroup",
        related_name="user_question_group",
        null=True
    )
    question: fields.ForeignKeyNullableRelation['Question'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Вопрос",
        model_name="models.Question",
        related_name="user_question",
        null=True
    )
    answer: fields.ForeignKeyNullableRelation['Answer'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Вопрос",
        model_name="models.Answer",
        related_name="user_answer",
        null=True
    )
    booking: fields.ForeignKeyNullableRelation['Booking'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Сделка",
        model_name="models.Booking",
        related_name="user_booking",
        null=True,
    )

    class Meta:
        table = "questionnaire_users_answers"


class UserAnswerRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий ответа пользователя
    """
    model = UserAnswer

    async def get_or_create_and_update(self, filters: dict, data: dict) -> None:
        """
        Получение или создание ответа пользователя с обновлением
        """
        model = await self.model.get_or_create(**filters)
        found_model: UserAnswer = model[0]

        for field, value in data.items():
            setattr(found_model, field, value)

        await found_model.save()
