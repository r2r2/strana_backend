from importlib import import_module

from pytest import fixture

from src.amocrm.repos import (
    AmocrmPipelineRepo,
    AmocrmPipeline,
    AmocrmGroupStatusRepo,
    AmocrmGroupStatus,
    AmocrmStatusRepo,
    AmocrmStatus,
)


@fixture(scope="function")
def amo_pipeline_repo() -> AmocrmPipelineRepo:
    pipeline_repo: AmocrmPipelineRepo = getattr(
        import_module("src.amocrm.repos"), "AmocrmPipelineRepo"
    )()
    return pipeline_repo


@fixture(scope="function")
def amo_group_status_repo() -> AmocrmGroupStatusRepo:
    group_status_repo: AmocrmGroupStatusRepo = getattr(
        import_module("src.amocrm.repos"), "AmocrmGroupStatusRepo"
    )()
    return group_status_repo


@fixture(scope="function")
def amo_status_repo() -> AmocrmStatusRepo:
    status_repo: AmocrmStatusRepo = getattr(
        import_module("src.amocrm.repos"), "AmocrmStatusRepo"
    )()
    return status_repo


@fixture(scope="function")
async def amo_pipeline(amo_pipeline_repo, faker) -> AmocrmPipeline:
    pipeline_data: dict = dict(
        name=faker.word(),
    )
    pipeline: AmocrmPipeline = await amo_pipeline_repo.create(data=pipeline_data)
    return pipeline


@fixture(scope="function")
async def amo_group_status(amo_group_status_repo, faker) -> AmocrmGroupStatus:
    group_status_data: dict = dict(
        name=faker.word(),
        color=faker.color(),
    )
    group_status: AmocrmGroupStatus = await amo_group_status_repo.create(
        data=group_status_data
    )
    return group_status


@fixture(scope="function")
async def amo_status(
    amo_status_repo, amo_pipeline, amo_group_status, faker
) -> AmocrmStatus:
    amo_status_data: dict = dict(
        name=faker.word(),
        pipeline_id=amo_pipeline.id,
        group_status_id=amo_group_status.id,
        color=faker.color(),
    )
    status: AmocrmStatus = await amo_status_repo.create(data=amo_status_data)
    return status


@fixture(scope="function")
async def amo_pipeline_1305043(amo_pipeline_repo, faker) -> AmocrmPipeline:
    pipeline_data: dict = dict(
        id=1305043,
        name="Продажи г. Тюмень",
    )
    pipeline: AmocrmPipeline = await amo_pipeline_repo.create(data=pipeline_data)
    return pipeline


@fixture(scope="function")
async def amo_group_status_booking(amo_group_status_repo, faker) -> AmocrmGroupStatus:
    group_status_data: dict = dict(
        name="Бронь",
        color=faker.color(),
    )
    group_status: AmocrmGroupStatus = await amo_group_status_repo.create(
        data=group_status_data
    )
    return group_status


@fixture(scope="function")
async def amo_status_1305043(
    amo_status_repo, amo_pipeline_1305043, amo_group_status_booking, faker
) -> AmocrmStatus:
    amo_status_data: dict = dict(
        id=21197641,
        name="Статус-Бронь-21197641-Тюмень-1305043",
        pipeline_id=amo_pipeline_1305043.id,
        group_status_id=amo_group_status_booking.id,
        color=faker.color(),
    )
    status: AmocrmStatus = await amo_status_repo.create(data=amo_status_data)
    return status
