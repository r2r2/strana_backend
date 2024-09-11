from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import Any

from pydantic import BaseModel

from src.core.common import StringEnum


class EnumCompatibilityCheck(Enum):
    @classmethod
    def is_compatible(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False


@unique
class Ability(EnumCompatibilityCheck, StringEnum):
    ADMIN = auto()
    EXTENDED_STATISTICS = auto()


@unique
class Role(EnumCompatibilityCheck, StringEnum):
    SCOUT = auto()
    BOOKMAKER = auto()
    SUPERVISOR = auto()

    @classmethod
    def _missing_(cls, value: Any) -> "Role | None":
        """Accept uppercase values when constructing instance"""
        if isinstance(value, str):
            for member in cls:
                if member.name == value:
                    return member

        return None


@unique
class Language(StringEnum):
    RU = auto()
    EN = auto()

    @classmethod
    def _missing_(cls, value: object) -> "Language":
        """Default value, e.g. Language("it") = Language.EN"""
        return cls.EN


@dataclass
class AuthPayload:
    id: int
    roles: list[Role]
    abilities: list[Ability]
    lang: Language

    @property
    def role(self) -> Role:
        priorities = (Role.SUPERVISOR, Role.BOOKMAKER, Role.SCOUT)
        self.roles.sort(key=lambda role: priorities.index(role))
        return self.roles[0]

    def has_ability(self, ability: Ability) -> bool:
        return ability in self.abilities


@unique
class PresenceStatus(StringEnum):
    ONLINE = auto()
    OFFLINE = auto()


@dataclass(kw_only=True, repr=True, eq=True)
class UserWithRoleDTO:
    user_id: int
    user_role: Role


@dataclass(kw_only=True, repr=True, eq=True)
class ChatUserDTO(UserWithRoleDTO):
    is_primary_member: bool

    def __hash__(self) -> int:
        return hash((self.user_id, self.user_role))


class UserData(BaseModel):
    id: int
    role: Role
    name: str
    scout_number: int | None
