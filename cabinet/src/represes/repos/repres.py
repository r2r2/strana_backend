from common import orm
from common.orm.mixins import CRUDMixin

from src.users.repos import User
from src.users.constants import UserType
from ..entities import BaseRepresRepo


class RepresRepo(BaseRepresRepo, CRUDMixin):
    """
    Репозиторий представителя
    """

    model = User
    q_builder: orm.QBuilder = orm.QBuilder(User)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(User)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(User)

    async def delete(self, repres: User) -> None:
        """
        Удаление представителя
        """
        if repres.type != UserType.REPRES:
            raise ValueError
        await repres.delete()
