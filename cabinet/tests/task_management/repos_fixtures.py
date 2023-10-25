import pytest
from importlib import import_module

from src.task_management.repos import (
    TaskChainRepo,
    TaskStatusRepo,
    TaskInstanceRepo,
    TaskStatus,
    TaskChain,
    TaskInstance,
)


@pytest.fixture(scope="function")
def task_chain_repo() -> TaskChainRepo:
    task_chain_repo: TaskChainRepo = getattr(import_module("src.task_management.repos"), "TaskChainRepo")()
    return task_chain_repo


@pytest.fixture(scope="function")
def task_status_repo() -> TaskStatusRepo:
    task_status_repo: TaskStatusRepo = getattr(import_module("src.task_management.repos"), "TaskStatusRepo")()
    return task_status_repo


@pytest.fixture(scope="function")
def task_instance_repo() -> TaskInstanceRepo:
    task_instance_repo: TaskInstanceRepo = getattr(import_module("src.task_management.repos"), "TaskInstanceRepo")()
    return task_instance_repo


@pytest.fixture(scope="function")
async def task_chain(task_chain_repo) -> TaskChain:
    # todo: add booking_substage, task_visibility, task_fields, booking_source
    task_chain: TaskChain = await task_chain_repo.create(
        data=dict(
            name="test_task_chain",
            sensei_pid=1,
        )
    )
    return task_chain


@pytest.fixture(scope="function")
async def task_status(task_status_repo, task_chain) -> TaskStatus:
    task_status: TaskStatus = await task_status_repo.create(
        data=dict(
            name="test_task_status",
            description="test_description",
            type="test_type",
            priority=1,
            slug="test_slug",
            tasks_chain_id=task_chain.id,
        )
    )
    return task_status


@pytest.fixture(scope="function")
async def task_status_2(task_status_repo, task_chain) -> TaskStatus:
    task_status: TaskStatus = await task_status_repo.create(
        data=dict(
            name="test_task_status_2",
            description="test_description_2",
            type="test_type_2",
            priority=1,
            slug="test_slug_2",
            tasks_chain_id=task_chain.id,
        )
    )
    return task_status


@pytest.fixture(scope="function")
async def task_instance(task_instance_repo, task_status, booking) -> TaskInstance:
    task_instance: TaskInstance = await task_instance_repo.create(
        data=dict(
            comment="test_comment",
            task_amocrmid=1,
            current_step="test_current_step",
            status_id=task_status.id,
            booking_id=booking.id,
        )
    )
    print(f'Created fixture task = {task_instance=} with id# {task_instance.id=}')
    return task_instance
