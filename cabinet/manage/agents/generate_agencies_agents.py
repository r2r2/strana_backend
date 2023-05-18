from copy import copy

from pytz import UTC
from sys import argv
from random import randint
from datetime import datetime, timedelta
from typing import Coroutine, Any, Union, Type

from tortoise import Tortoise

from config import tortoise_config
from src.users import repos as users_repos
from src.agents import repos as agents_repos
from src.floors import repos as floors_repos
from src.booking import repos as booking_repos
from src.represes import repos as represes_repos
from src.agencies import repos as agencies_repos
from src.projects import repos as projects_repos
from src.buildings import repos as buildings_repos
from src.properties import repos as properties_repos


from src.users import constants as users_constants
from src.booking import constants as booking_constants
from src.properties import constants as properties_constants

from ..decorators import skip_integrity


class GenerateAgenciesAgents(object):
    """
    Генерация тестовых агентов для агенства
    """

    email_flag: str = "--email"
    quantity_flag: str = "--quantity"

    def __init__(self):
        self.user_repo: users_repos.UserRepo = users_repos.UserRepo()
        self.check_repo: users_repos.CheckRepo = users_repos.CheckRepo()
        self.agent_repo: agents_repos.AgentRepo = agents_repos.AgentRepo()
        self.floor_repo: floors_repos.FloorRepo = floors_repos.FloorRepo()
        self.repres_repo: represes_repos.RepresRepo = represes_repos.RepresRepo()
        self.agency_repo: agencies_repos.AgencyRepo = agencies_repos.AgencyRepo()
        self.booking_repo: booking_repos.BookingRepo = booking_repos.BookingRepo()
        self.project_repo: projects_repos.ProjectRepo = projects_repos.ProjectRepo()
        self.building_repo: buildings_repos.BuildingRepo = buildings_repos.BuildingRepo()
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()

        self._counter: int = 0
        self._quantity: int = 0
        self._email: str = str()
        self._phone: str = str()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    def __await__(self) -> Coroutine:
        return self().__await__()

    async def __call__(self, *args, **kwargs):
        await self.orm_class.init(config=self.orm_config)
        self._counter: int = 0
        self._quantity: int = 0
        self._email: str = str()
        self._phone: str = str()
        if self.email_flag in argv and self.quantity_flag in argv:
            email_index: int = argv.index(self.email_flag)
            quantity_index: int = argv.index(self.quantity_flag)
            if len(argv) >= email_index + 2:
                self._email: str = argv[email_index + 1]
                quantity: int = int(argv[quantity_index + 1])
                filters: dict[str, Any] = dict(email=self._email)
                repres: agents_repos.User = await self.repres_repo.retrieve(filters=filters)
                filters: dict[str, Any] = dict(inn="22814881337")
                agency: agencies_repos.Agency = await self.agency_repo.retrieve(filters=filters)
                if not agency:
                    data: dict[str, Any] = dict(
                        type="OOO",
                        city="Тюмень",
                        inn="22814881337",
                        is_approved=True,
                        name="Стреттен Оакмонт",
                    )
                    agency: agencies_repos.Agency = await self.agency_repo.create(data=data)
                elif not agency.is_approved:
                    data: dict[str, Any] = dict(
                        type="OOO", city="Тюмень", is_approved=True, name="Стреттен Оакмонт"
                    )
                    agency: agencies_repos.Agency = await self.agency_repo.update(agency, data=data)
                if repres:
                    data: dict[str, Any] = dict(
                        name="Джордан",
                        surname="Белфорд",
                        patronymic="Росс",
                        agency_id=agency.id,
                        maintained_id=agency.id,
                    )
                    if repres.type != users_constants.UserType.REPRES:
                        data.update(dict(type=users_constants.UserType.REPRES))
                    await self.repres_repo.update(repres, data=data)
                    self._phone: str = repres.phone
                    filters: dict[str, Any] = dict(
                        phone__icontains=self._phone, type=users_constants.UserType.CLIENT
                    )
                    users: list[users_repos.User] = await self.user_repo.list(filters=filters)
                    filters: dict[str, Any] = dict(
                        phone__icontains=self._phone, type=users_constants.UserType.AGENT
                    )
                    agents: list[agents_repos.User] = await self.agent_repo.list(filters=filters)
                    filters: dict[str, Any] = dict(slug__icontains=self._email)
                    projects: list[projects_repos.Project] = await self.project_repo.list(
                        filters=filters
                    )
                    for user in users:
                        if user.email != self._email:
                            await self.user_repo.delete(user)
                    for agent in agents:
                        if agent.email != self._email:
                            await self.agent_repo.delete(agent)
                    for project in projects:
                        await self.project_repo.delete(project)
                    for i in range(quantity):
                        async for user in self.generate_main(repres=repres):
                            for j in range(randint(4, 7)):
                                await self.generate_related(user=user)
                                self._counter += 1
        await self.orm_class.close_connections()

    async def generate_main(self, repres: represes_repos.User) -> users_repos.User:
        agent: agents_repos.User = await self._generate_agent(repres=repres)
        for i in range(randint(3, 8)):
            yield await self._generate_user(agent=agent)

    @skip_integrity
    async def generate_related(self, user: users_repos.User) -> booking_repos.Booking:
        project: projects_repos.Project = await self._generate_project()
        building: buildings_repos.Building = await self._generate_building(project=project)
        floor: floors_repos.Floor = await self._generate_floor(building=building)
        property: properties_repos.Property = await self._generate_property(
            floor=floor, project=project, building=building
        )
        booking: booking_repos.Booking = await self._generate_booking(
            user=user, floor=floor, project=project, building=building, property=property
        )
        return booking

    @skip_integrity
    async def _generate_project(self) -> Union[projects_repos.Project, None]:
        data: dict[str, Any] = dict(
            slug=f"{self._email}_test_{self._counter}_project_slug",
            name=f"{self._email.replace('@', '').replace('.', '').upper()}_{self._counter}_PROJECT",
        )
        return await self.project_repo.create(data=data)

    @skip_integrity
    async def _generate_building(
        self, project: projects_repos.Project
    ) -> Union[buildings_repos.Building, None]:
        if project:
            data: dict[str, Any] = dict(
                project_id=project.id,
                booking_period=randint(10, 30),
                booking_price=randint(20000, 30000),
                name=f"{self._email.replace('@', '').replace('.', '').upper()}_{self._counter}_BUILDING",
            )
            return await self.building_repo.create(data=data)

    @skip_integrity
    async def _generate_floor(
        self, building: buildings_repos.Building
    ) -> Union[floors_repos.Floor, None]:
        if building:
            data: dict[str, Any] = dict(number=randint(1, 25), building_id=building.id)
            return await self.floor_repo.create(data=data)

    @skip_integrity
    async def _generate_property(
        self,
        floor: floors_repos.Floor,
        project: projects_repos.Project,
        building: buildings_repos.Building,
    ) -> Union[properties_repos.Property, None]:
        if floor and project and building:
            focus: int = randint(1, 4)

            if focus == 1:
                type: str = properties_constants.PropertyTypes.PARKING
            elif focus == 2:
                type: str = properties_constants.PropertyTypes.COMMERCIAL
            elif focus == 3:
                type: str = properties_constants.PropertyTypes.COMMERCIAL_APARTMENT
            else:
                type: str = properties_constants.PropertyTypes.FLAT

            data: dict[str, Any] = dict(
                type=type,
                floor_id=floor.id,
                rooms=randint(1, 8),
                area=randint(10, 300),
                project_id=project.id,
                building_id=building.id,
                discount=randint(100000, 1000000),
                price=randint(1000000, 100000000),
                original_price=randint(1000000, 100000000),
                number=randint(128, 938312412),
                status=properties_constants.PropertyStatuses.FREE,
                premise=properties_constants.PremiseType.RESIDENTIAL,
                article=f"{self._email.replace('@', '').replace('.', '').upper()}_{self._counter}",
            )
            return await self.property_repo.create(data=data)

    @skip_integrity
    async def _generate_user(self, agent: agents_repos.User) -> Union[users_repos.User, None]:
        if agent:
            focus: int = randint(0, 1)

            if focus:
                agent_id: int = agent.id
                agency_id: Union[int, None] = agent.agency_id
            else:
                agent_id = None
                agency_id = None

            data: dict[str, Any] = dict(
                is_active=True,
                agent_id=agent_id,
                agency_id=agency_id,
                passport_series="1234",
                passport_number="111111",
                name=f"Имя_{self._counter}",
                work_start=datetime.now(tz=UTC),
                surname=f"Фамилия_{self._counter}",
                type=users_constants.UserType.CLIENT,
                phone=f"{self._phone}{self._counter}",
                patronymic=f"Отчество_{self._counter}",
                birth_date=datetime.now(tz=UTC) - timedelta(weeks=2000),
                work_end=datetime.now(tz=UTC) + timedelta(days=randint(10, 30)),
                email=f"{self._email.replace('@', '').replace('.', '')}_test_{self._counter}@gmail.com",
            )
            user: users_repos.User = await self.user_repo.create(data=data)

            if focus:
                data: dict[str, Any] = dict(
                    user_id=user.id,
                    agent_id=agent.id,
                    agency_id=agent.agency_id,
                    requested=datetime.now(tz=UTC),
                    status=users_constants.UserStatus.UNIQUE,
                )
            else:
                data: dict[str, Any] = dict(
                    agency_id=None,
                    user_id=user.id,
                    agent_id=agent.id,
                    requested=datetime.now(tz=UTC),
                    status=users_constants.UserStatus.NOT_UNIQUE,
                )

            await self.check_repo.create(data=data)

            return user

    @skip_integrity
    async def _generate_booking(
        self,
        user: users_repos.User,
        floor: floors_repos.Floor,
        project: projects_repos.Project,
        building: buildings_repos.Building,
        property: properties_repos.Property,
    ) -> Union[booking_repos.Booking, None]:
        if user and floor and project and building and property:
            focus: int = randint(1, 7)

            if focus == 1:
                amocrm_stage: str = booking_constants.BookingStages.START
            elif focus == 2:
                amocrm_stage: str = booking_constants.BookingStages.BOOKING
            elif focus == 3:
                amocrm_stage: str = booking_constants.BookingStages.DDU_PROCESS
            elif focus == 4:
                amocrm_stage: str = booking_constants.BookingStages.DDU_SIGNING
            elif focus == 5:
                amocrm_stage: str = booking_constants.BookingStages.DDU_REGISTER
            elif focus == 6:
                amocrm_stage: str = booking_constants.BookingStages.DDU_FINISHED
            else:
                amocrm_stage: str = booking_constants.BookingStages.DDU_UNREGISTERED

            data: dict[str, Any] = dict(
                user_id=user.id,
                price_payed=True,
                floor_id=floor.id,
                params_checked=True,
                personal_filled=True,
                project_id=project.id,
                agent_id=user.agent_id,
                contract_accepted=True,
                building_id=building.id,
                property_id=property.id,
                commission=randint(1, 10),
                amocrm_stage=amocrm_stage,
                active=bool(randint(0, 1)),
                agency_id=user.agency_id,
                decremented=bool(randint(0, 1)),
                start_commission=randint(10, 15),
                commission_value=randint(20000, 60000),
                until=datetime.now(tz=UTC) + timedelta(days=120),
            )
            return await self.booking_repo.create(data=data)

    @skip_integrity
    async def _generate_agent(self, repres: represes_repos.User) -> agents_repos.User:
        data: dict[str, Any] = dict(
            is_active=True,
            agency_id=repres.agency_id,
            name=f"Имя_{self._counter}",
            is_approved=bool(randint(0, 1)),
            surname=f"Фамилия_{self._counter}",
            type=users_constants.UserType.AGENT,
            phone=f"{self._phone}{self._counter}1",
            patronymic=f"Отчество_{self._counter}",
            birth_date=datetime.now(tz=UTC) - timedelta(weeks=2000),
            email=f"{self._email.replace('@', '').replace('.', '')}_test_agent_{self._counter}@gmail.com",
        )
        agent: users_repos.User = await self.agent_repo.create(data=data)

        return agent
