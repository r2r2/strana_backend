from typing import Any, Union, Callable
from asyncio import Future, Task, create_task


def exit_manager_callback(request: Any) -> Callable[[Union[Task, Future]], None]:
    """
    Callback for context manager exit
    """

    def callback(task_or_future: Union[Task, Future]) -> None:
        create_task(request.close())

    return callback
