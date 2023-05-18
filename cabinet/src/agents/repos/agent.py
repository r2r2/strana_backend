from common import orm
from common.orm.mixins import GenericMixin

from src.users.repos import User
from ..entities import BaseAgentRepo


class AgentRepo(BaseAgentRepo, GenericMixin):
    """
    Репозиторий агента
    """
    model = User
    q_builder: orm.QBuilder = orm.QBuilder(User)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(User)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(User)
