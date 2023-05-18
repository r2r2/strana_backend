from common.orm.mixins import ExistsMixin, GenericMixin
from tortoise import Model, fields

from ..entities import BaseUserRepo
from ..mixins import UserRepoFacetsMixin, UserRepoSpecsMixin


class FakeUserPhone(Model):
    """
    Тестовые телефоны пользователей (аутентификация без запроса в СМС центр)
    """
    id: int = fields.IntField(description="ID", pk=True, index=True)
    phone: str = fields.CharField(description="Номер телефона", max_length=20, index=True)
    code: str = fields.CharField(description="Код", max_length=4, default="9999")

    def __str__(self) -> str:
        return self.phone

    class Meta:
        table = "users_test_user_phones"


class FakeUserPhoneRepo(BaseUserRepo, UserRepoSpecsMixin, UserRepoFacetsMixin, GenericMixin, ExistsMixin):
    """
    Репозиторий тестовых телефонов пользователей
    """
    model = FakeUserPhone
