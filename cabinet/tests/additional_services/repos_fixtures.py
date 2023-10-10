from importlib import import_module

from pytest import fixture

from src.additional_services.repos import (
    AdditionalServiceRepo as ServiceRepo,
    AdditionalService as Service,
    AdditionalServiceTypeRepo as ServiceTypeRepo,
    AdditionalServiceType as ServiceType,
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceCategory as Category,
    AdditionalServiceConditionRepo as ConditionRepo,
    AdditionalServiceCondition as Condition,
    AdditionalServiceConditionStepRepo as ConditionStepRepo,
    AdditionalServiceConditionStep as ConditionStep,
    AdditionalServiceTicketRepo as TicketRepo,
    AdditionalServiceTicket as Ticket,
    AdditionalServiceGroupStatusRepo as GroupStatusRepo,
    AdditionalServiceGroupStatus as GroupStatus,
)


@fixture(scope="function")
def service_category_repo() -> CategoryRepo:
    category_repo: CategoryRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceCategoryRepo"
    )()
    return category_repo


@fixture(scope="function")
async def service_category(service_category_repo, faker) -> Category:
    service_category_data: dict = dict(
        title=faker.word(),
    )
    service_category: Category = await service_category_repo.create(
        data=service_category_data
    )
    return service_category


@fixture(scope="function")
async def un_active_service_category(service_category_repo, faker) -> Category:
    un_active_service_category_data: dict = dict(
        title=faker.word(),
        active=False,
    )
    un_active_service_category: Category = await service_category_repo.create(
        data=un_active_service_category_data
    )
    return un_active_service_category


@fixture(scope="function")
def service_type_repo() -> ServiceTypeRepo:
    service_type_repo: ServiceTypeRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceTypeRepo"
    )()
    return service_type_repo


@fixture(scope="function")
def service_condition_repo() -> ConditionRepo:
    service_condition_repo: ConditionRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceConditionRepo"
    )()
    return service_condition_repo


@fixture(scope="function")
async def service_condition(service_condition_repo, faker) -> Condition:
    service_condition_data: dict = dict(
        title=faker.word(),
    )
    service_condition: Condition = await service_condition_repo.create(
        data=service_condition_data
    )
    return service_condition


@fixture(scope="function")
def service_repo() -> ServiceRepo:
    service_repo: ServiceRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceRepo"
    )()
    return service_repo


@fixture(scope="function")
async def service_type(service_type_repo, faker) -> ServiceType:
    service_type_data: dict = dict(
        title=faker.word(),
    )
    service_type: ServiceType = await service_type_repo.create(data=service_type_data)
    return service_type


@fixture(scope="function")
def service_repo() -> ServiceRepo:
    service_repo: ServiceRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceRepo"
    )()
    return service_repo


@fixture(scope="function")
async def active_service(
    service_repo, faker, service_category, service_condition, service_type
) -> Service:
    service_data: dict = dict(
        title=faker.word(),
        image_preview=faker.file_path(category="image", extension="jpg"),
        image_detailed=faker.file_path(category="image", extension="jpg"),
        announcement=faker.catch_phrase(),
        description=faker.text(),
        hint=faker.text(),
        category_id=service_category.id,
        kind_id=service_type.id,
        condition_id=service_condition.id,
    )
    service: Service = await service_repo.create(data=service_data)
    return service


@fixture(scope="function")
async def un_active_service(
    service_repo, faker, service_category, service_condition, service_type
) -> Service:
    service_data: dict = dict(
        title=faker.word(),
        image_preview=faker.file_path(category="image", extension="jpg"),
        image_detailed=faker.file_path(category="image", extension="jpg"),
        announcement=faker.catch_phrase(),
        description=faker.text(),
        hint=faker.text(),
        category_id=service_category.id,
        kind_id=service_type.id,
        condition_id=service_condition.id,
        active=False,
    )
    service: Service = await service_repo.create(data=service_data)
    return service


@fixture(scope="function")
def service_step_repo() -> ConditionStepRepo:
    service_step_repo: ConditionStepRepo = getattr(
        import_module("src.additional_services.repos"),
        "AdditionalServiceConditionStepRepo",
    )()
    return service_step_repo


@fixture(scope="function")
def group_status_repo() -> GroupStatusRepo:
    group_status_repo: GroupStatusRepo = getattr(
        import_module("src.additional_services.repos"),
        "AdditionalServiceGroupStatusRepo",
    )()
    return group_status_repo


@fixture(scope="function")
async def group_status(group_status_repo, faker) -> GroupStatus:
    group_status_data: dict = dict(
        name=faker.word(),
        slug="ticket_sent",
    )
    group_status: GroupStatus = await group_status_repo.create(data=group_status_data)
    return group_status


@fixture(scope="function")
async def service_steps(
    service_step_repo, service_condition, faker
) -> list[ConditionStep]:
    steps_list_data: list = []
    for condition_count in range(6):
        if condition_count % 2 == 0:
            steps_list_data.append(
                dict(
                    description=faker.text(),
                    active=True,
                    condition_id=service_condition.id,
                )
            )
        else:
            steps_list_data.append(
                dict(
                    description=faker.text(),
                    active=False,
                    condition_id=service_condition.id,
                )
            )

    condition_steps: list = []
    for step_data in steps_list_data:
        step: ConditionStep = await service_step_repo.create(data=step_data)
        condition_steps.append(step)
    return condition_steps


@fixture(scope="function")
def service_ticket_repo() -> TicketRepo:
    service_ticket_repo: TicketRepo = getattr(
        import_module("src.additional_services.repos"), "AdditionalServiceTicketRepo"
    )()
    return service_ticket_repo


@fixture(scope="function")
async def service_ticket_single(
    service_ticket_repo, active_service, user, amo_status, booking, faker
) -> Ticket:
    ticket_data: dict = dict(
        full_name=faker.name(),
        phone=faker.phone_number(),
        service_id=active_service.id,
        booking_id=booking.id,
        user_id=user.id,
        status_id=amo_status.id,
    )
    ticket: Ticket = await service_ticket_repo.create(data=ticket_data)
    return ticket
