from common import orm
from common.orm.mixins import ReadWriteMixin

from src.users.repos import User
from ..entities import BaseAdminRepo


class AdminRepo(BaseAdminRepo, ReadWriteMixin):
    """
    Репозиторий администратора
    """
    model = User
    q_builder: orm.QBuilder = orm.QBuilder(User)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(User)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(User)
