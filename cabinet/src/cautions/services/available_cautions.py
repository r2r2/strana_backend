from typing import Any, List, Type

from src.cautions.entities import BaseCautionService
from src.cautions.repos.caution import Caution, CautionRepo
from src.users.exceptions import UserNotFoundError
from src.users.repos import User, UserRepo
from tortoise.fields.relational import RelationalField


class AvailableCautionsForUserService(BaseCautionService):
    """Получение доступных уведомлений для пользователя"""

    def __init__(
        self,
        user_repo: Type[UserRepo],
        caution_repo: Type[CautionRepo],
    ):
        self.user_repo = user_repo()
        self.caution_repo = caution_repo()

    async def __call__(self, user_id: int) -> List[Caution]:
        """Возвращает список предупреждений для юзера, отфильтрованный по полю priority.
        user_repo - здесь используется, как способ получения любого типа пользователей, не только клиентов
        """
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError
        user_type: Any = user.type

        cautions: List[Caution] = await self.caution_repo.execute(
            self.caution_sql(user_id, await self._fields(), user_type.value)
        )

        return cautions

    async def _fields(self):
        """ Получение названия столбцов для передачи в sql-запрос
        note: кроме поля id
        """
        tmp_object: Caution = await self.caution_repo.retrieve(filters=dict())
        fields = tmp_object._meta.fields_map
        result = []
        for key, item in fields.items():
            # скипаем объекты связей
            if issubclass(type(item), RelationalField):
                continue
            # поле id будет в запросе задаваться через "AS"
            if key == "id":
                continue
            result.append(key)
        return result

    @staticmethod
    def caution_sql(user_id: int, fields: list, user_type: str):
        """Строка sql-запроса логики получения предупреждений для пользователя, которые ему еще не были показаны"""
        return f""" SELECT {", ".join(["c1.id AS id"] + fields)}
        FROM cautions_caution c1
        LEFT JOIN users_caution_mute c2 ON c2.caution_id = c1.id AND c2.user_id = {user_id}
        WHERE c2.caution_id IS NULL AND c1.roles::jsonb ? '{user_type}'
        AND c1.expires_at > now() AND c1.is_active IS TRUE
        ORDER BY c1.priority
        """

