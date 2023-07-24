from tortoise import Model, fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseUserRepo


class UserRole(Model):
    """
    Роль пользователя
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(max_length=150, description="Название роли", null=True)
    slug: str = fields.CharField(max_length=50, description="slug", null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "users_roles"


class UserRoleRepo(BaseUserRepo, ReadWriteMixin):
    """
    Репозиторий роли пользователя
    """
    model = UserRole
