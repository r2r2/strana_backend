from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from common import cfields, orm
from common.orm.mixins import ExistsMixin, GenericMixin
from src.agencies.repos import Agency
from src.projects.repos import Project
from src.properties.constants import PropertyTypes
from src.properties.repos import Property
from tortoise import Model, fields
from tortoise.exceptions import IntegrityError
from tortoise.fields import ForeignKeyNullableRelation, ManyToManyRelation, ForeignKeyRelation

from ..constants import DutyType, UserType
from ..entities import BaseUserRepo
from ..mixins import UserRepoFacetsMixin, UserRepoSpecsMixin


class User(Model):
    """
    Пользователь
    """

    types = UserType()
    duty_types = DutyType()

    id: int = fields.IntField(description="ID", pk=True, index=True)
    tags: Union[list, dict] = fields.JSONField(description="Тэги", null=True)
    type: Optional[str] = cfields.CharChoiceField(
        description="Тип", max_length=20, default=UserType.CLIENT, choice_class=UserType, null=True
    )
    role: ForeignKeyRelation["UserRole"] = fields.ForeignKeyField(
        description="Роль пользователя",
        model_name="models.UserRole",
        on_delete=fields.SET_NULL,
        related_name="users",
        null=True
    )
    interested_type: Optional[str] = cfields.CharChoiceField(
        description="Интересующий тип недвижимости",
        choice_class=PropertyTypes,
        max_length=20,
        null=True,
    )
    duty_type: Optional[str] = cfields.CharChoiceField(
        description="Тип должности", max_length=20, choice_class=DutyType, null=True
    )

    username: Optional[str] = fields.CharField(
        description="Имя пользователя", max_length=100, null=True
    )
    password: Optional[str] = fields.CharField(description="Пароль", max_length=200, null=True)
    one_time_password: Optional[str] = fields.CharField(
        description="Единоразовый пароль", max_length=200, null=True
    )

    email: Optional[str] = fields.CharField(
        description="Email", max_length=100, null=True, index=True
    )
    phone: Optional[str] = fields.CharField(
        description="Номер телефона", max_length=20, null=True, index=True
    )
    change_email: Optional[str] = fields.CharField(
        description="Email для смены", max_length=100, null=True
    )
    change_phone: Optional[str] = fields.CharField(
        description="Номер телефона для смены", max_length=20, null=True
    )

    code: Optional[str] = fields.CharField(description="Код", max_length=4, null=True)
    code_time: Optional[datetime] = fields.DatetimeField(
        description="Время отправки кода", null=True
    )

    token: Optional[UUID] = fields.UUIDField(description="Токен", null=True)
    email_token: Optional[str] = fields.CharField(
        description="Токен email", max_length=100, null=True
    )
    phone_token: Optional[str] = fields.CharField(
        description="Токен номера телефона", max_length=100, null=True
    )
    discard_token: Optional[str] = fields.CharField(
        description="Токен сброса", max_length=100, null=True
    )
    change_phone_token: Optional[str] = fields.CharField(
        description="Токен обновления номера телефона", max_length=100, null=True
    )
    change_email_token: Optional[str] = fields.CharField(
        description="Токен обновления email", max_length=100, null=True
    )

    reset_time: Optional[datetime] = fields.DatetimeField(
        description="Время валидности ресета", null=True
    )

    work_start: Optional[date] = fields.DateField(description="Начало работ", null=True)
    work_end: Optional[date] = fields.DateField(description="Окончание работ", null=True)

    name: Optional[str] = fields.CharField(description="Имя", max_length=50, null=True, index=True)
    surname: Optional[str] = fields.CharField(
        description="Фамилия", max_length=50, null=True, index=True
    )
    patronymic: Optional[str] = fields.CharField(
        description="Отчество", max_length=50, null=True, index=True
    )
    birth_date: Optional[date] = fields.DateField(description="Дата рождения", null=True)

    passport_series: Optional[str] = fields.CharField(
        description="Серия паспорта", max_length=20, null=True
    )
    passport_number: Optional[str] = fields.CharField(
        description="Номер паспорта", max_length=20, null=True
    )

    is_deleted: bool = fields.BooleanField(description="Удален", default=False)
    is_active: bool = fields.BooleanField(description="Активный", default=False)
    is_superuser: bool = fields.BooleanField(description="Супер", default=False)
    is_approved: bool = fields.BooleanField(description="Одобрен", default=False)
    is_imported: bool = fields.BooleanField(description="Импортирован", default=False)
    is_contracted: bool = fields.BooleanField(description="Договор принят", default=False)
    is_onboarded: bool = fields.BooleanField(description="Онбординг просмотрен", default=False)
    is_test_user: bool = fields.BooleanField(
        description="Тестовый пользователь",
        default=False
    )
    receive_admin_emails: bool = fields.BooleanField(
        description="Получать письма администратора",
        default=False
    )
    sms_send: bool = fields.BooleanField(description="СМС отправлено", default=False)

    amocrm_id: Optional[int] = fields.BigIntField(description="ID AmoCRM", null=True)

    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="users",
        null=True,
    )
    maintained: ForeignKeyNullableRelation[Agency] = fields.OneToOneField(
        description="Главный агентства",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="maintainer",
        null=True,
    )
    agent: ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="users",
        null=True,
    )
    interested_project: ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Интересующий проект",
        model_name="models.Project",
        related_name="interested_user",
        on_delete=fields.SET_NULL,
        null=True,
    )
    interested: ManyToManyRelation[Property] = fields.ManyToManyField(
        description="Интересующие объекты",
        model_name="models.Property",
        related_name="interested_users",
        on_delete=fields.SET_NULL,
        through="users_interests",
        forward_key="property_id",
        backward_key="user_id",
        null=True,
    )
    checkers: ManyToManyRelation["User"] = fields.ManyToManyField(
        description="Проверяющие",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        through="users_checks",
        related_name="users_on_check",
        forward_key="agent_id",
        backward_key="user_id",
        null=True,
    )

    is_brokers_client: bool = fields.BooleanField(description="Клиент брокера", default=False)
    is_independent_client: bool = fields.BooleanField(  # Логинился через ЛК в качестве клиента
        description="Самостоятельный клиент", default=False
    )

    created_at: datetime = fields.DatetimeField(
        description="Дата и время регистрации в базе", auto_now_add=True
    )
    auth_first_at: Optional[datetime] = fields.DatetimeField(
        description="Дата и время первой авторизации", null=True
    )
    interested_sub: bool = fields.BooleanField(description="Подписка на избранное", default=False)

    assignation_comment: Optional[str] = fields.TextField(
        description="Комментарий при закреплении клиента", null=True
    )

    users_checks: fields.ReverseRelation["Check"]
    bookings: fields.ReverseRelation["Booking"]
    users_pinning_status: fields.ReverseRelation["UserPinningStatus"]
    agent_confirm_client_assign: fields.ReverseRelation["ConfirmClientAssign"]
    client_confirm_client_assign: fields.ReverseRelation["ConfirmClientAssign"]
    agency_id: Optional[int]
    agent_id: Optional[int]
    maintained_id: Optional[int]

    def __str__(self) -> str:
        representation: str = str()
        if self.surname and self.name:
            representation: str = (
                f"{self.surname.capitalize()}."
                f"{self.name[0].capitalize()}."
                f"{(self.patronymic[0].capitalize() + '.') if self.patronymic else str()}"
            )
        elif self.phone:
            representation: str = self.phone
        elif self.email:
            representation: str = self.email
        return representation

    @property
    def full_name(self) -> str:
        """Полное имя"""
        full_name: str = f"{self.surname} {self.name} "
        if self.patronymic:
            full_name += f"{self.patronymic}"
        return full_name.strip()

    @property
    def is_fired(self) -> Optional[bool]:
        """
        Агент уволен
        """
        if self.type != UserType.AGENT:
            return None
        return self.agency_id is None

    class Meta:
        table = "users_user"
        unique_together = (
            ("type", "phone"),
            ("type", "email"),
            ("type", "username"),
        )
        ordering = ["-created_at"]


class UserRepo(BaseUserRepo, UserRepoSpecsMixin, UserRepoFacetsMixin, GenericMixin, ExistsMixin):
    """
    Репозиторий пользователя
    """
    model = User
    q_builder: orm.QBuilder = orm.QBuilder(User)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(User)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(User)

    async def update(self, model: User, data: dict[str, Any]) -> Union[User, None]:
        """
        Обновление пользователя
        """
        for field, value in data.items():
            setattr(model, field, value)
        try:
            await model.save()
        except IntegrityError:
            model = None
        return model

    async def add_m2m(self, model: User, relation: str, instances: list[Model]) -> None:
        """
        Добавление связи М2М
        """
        if instances:
            await getattr(model, relation).add(*instances)

    async def rm_m2m(self, model: User, relation: str, instances: list[Model]) -> None:
        """
        Удаление связи М2М
        """
        if instances:
            await getattr(model, relation).remove(*instances)

    async def fetch_or_create(self, data: dict[str, Any]) -> User:
        """
        Создание пользователя, если не существует с таким телефоном или email-ом
        """
        q_filters = [
            self.q_builder(or_filters=[dict(phone=data.get('phone')), dict(email__iexact=data.get('email'))])
        ]
        user = await self.retrieve(filters={}, q_filters=q_filters)

        if not user:
            user = await super().create(data)
        return user
