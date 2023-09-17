import pytest
from importlib import import_module

from src.task_management.repos import TaskChainRepo, TaskStatusRepo, TaskInstanceRepo


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
