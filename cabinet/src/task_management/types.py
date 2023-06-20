from typing import NewType

from tortoise import Tortoise

TaskManagementORM = NewType('TaskManagementORM', Tortoise)
