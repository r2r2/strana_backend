import manage
from sys import argv
from uvicorn import run
from config import uvicorn_config
from asyncio import get_event_loop
from typing import Any, Callable, Coroutine, Union


def default(
    actions: dict[str, Callable[..., Any]], coroutines: dict[str, Callable[..., Coroutine]]
) -> None:

    available_actions: str = str()
    available_coroutines: str = str()
    for action, _ in actions.items():
        available_actions += "* " + action + "\n"
    for coroutine, _ in coroutines.items():
        available_coroutines += "* " + coroutine + "\n"
    print(
        (
            f"You must specify one "
            f"of the following actions: \n{available_actions}"
            f"or coroutines (with '-a' argv): \n{available_coroutines}"
        )
    )
    exit()


def unknown(
    actions: dict[str, Callable[..., Any]], coroutines: dict[str, Callable[..., Coroutine]]
) -> None:
    available_actions: str = str()
    available_coroutines: str = str()
    for action, _ in actions.items():
        available_actions += "* " + action + "\n"
    for coroutine, _ in coroutines.items():
        available_coroutines += "* " + coroutine + "\n"
    print(
        (
            f"Unknown command called.\n"
            f"Available actions: \n{available_actions}"
            f"Available coroutines (with '-a' argv): \n{available_coroutines}"
        )
    )
    exit()


def sync_main(
    actions: dict[str, Callable[..., Any]], coroutines: dict[str, Callable[..., Coroutine]]
) -> None:
    if not len(argv) > 1:
        default(actions, coroutines)
    action: Union[Callable[..., Any], None] = actions.get(argv[1], None)
    if not action:
        unknown(actions, coroutines)
    action()


async def async_main(
    actions: dict[str, Callable[..., Any]], coroutines: dict[str, Callable[..., Coroutine]]
) -> None:
    if not len(argv) > 1:
        default(actions, coroutines)
    coroutine: Union[Callable[..., Coroutine], None] = coroutines.get(argv[1], None)
    if not coroutine:
        unknown(actions, coroutines)
    await coroutine(argv[-1])


actions_map: dict[str, Callable[..., Any]] = {"runserver": lambda: run(**uvicorn_config)}

coroutines_map: dict[str, Callable[..., Coroutine]] = {
    "sendbookingemail": manage.SendBookingEmail(),
    "sendtestmail": manage.SendTestEmail(),
    "generateagentsusers": manage.GenerateAgentsUsers(),
    "updateproperties": manage.UpdatePropertiesManage(),
    "checkpropertiesunique": manage.CheckPropertiesUniqueManage(),
    "updateinterestproperties": manage.UpdateInterestPropertiesManage(),
    "generateagenciesagents": manage.GenerateAgenciesAgents(),
    "checkprofitbase": manage.CheckPropertyProfitbase(),
    "historyprofitbase": manage.HistoryPropertyProfitbase(),
    "dealsprofitbase": manage.PropertyDealsPropertyProfitbase(),
    "unbookingprofitbase": manage.UnbookingPropertyProfitbase(),
    "closeoldbookings": manage.CloseOldBookings(),
    "unknown_participants": manage.CheckParticipantsNotInDB(),
    "remove_slash_in_plan": manage.RemoveSlashInPlan(),
    "check_client_interests": manage.CheckClientInterestManage(),
    "compare_type_and_role": manage.CompareTypeAndRole(),
}


if __name__ == "__main__":
    if "-a" in argv:
        # poetry run python3.11 manage.py remove_slash_in_plan -a
        loop: Any = get_event_loop()
        loop.run_until_complete(async_main(actions_map, coroutines_map))
    else:
        sync_main(actions_map, coroutines_map)
