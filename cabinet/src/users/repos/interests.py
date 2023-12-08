from typing import Optional

from common import cfields
from common.orm.mixins import CRUDMixin, CountMixin
from src.users.constants import SlugType
from src.users.entities import BaseUserRepo
from tortoise import Model, fields


class UsersInterests(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User',
        related_name='favorites',
        on_delete=fields.CASCADE,
        description='Пользователь избранного'
    )
    property = fields.ForeignKeyField(
        'models.Property',
        related_name='favorites',
        on_delete=fields.CASCADE,
        description='Бронирование избранного',
        null=True,
    )
    interest_final_price: Optional[int] = fields.BigIntField(description="Конечная цена", null=True)
    interest_status: Optional[int] = fields.SmallIntField(description="Статус", null=True)
    slug: [str] = cfields.CharChoiceField(
        description="Slug", max_length=10, default=SlugType.MINE, choice_class=SlugType, null=True, index=True
    )
    interest_special_offers: Optional[str] = fields.TextField(description="Акции", null=True)
    created_by = fields.ForeignKeyField(
        'models.User',
        related_name='created_favorites',
        on_delete=fields.CASCADE,
        descriptio='Кем создано',
        null=True,
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        description='Время добавления избранного'
    )

    class Meta:
        table = 'users_interests'


class InterestsRepo(BaseUserRepo, CRUDMixin, CountMixin):
    """
    Репозиторий для избранного
    """
    model = UsersInterests

    async def add(
            self,
            user: 'Model',
            interest: 'Model',
            slug_type: Optional[str] = SlugType.MANAGER,
            created_by: Optional['Model'] = None,
    ):
        """Save favorites with custom fields"""

        await self.model(
            user=user,
            property=interest,
            created_by=created_by,
            interest_final_price=interest.final_price,
            interest_status=interest.status.value,
            interest_special_offers=interest.special_offers,
            slug=slug_type
        ).save()
