from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.http.serializers.common import CommaSeparatedNumbers, PaginatedResponse
from src.api.http.serializers.users import GrantRequest, RevokeRequest
from src.controllers.users import UsersController
from src.entities.users import AuthPayload, Role, UserData
from src.modules.auth.dependencies import UserAuth, admin_required, supervisor_required

users_router = APIRouter(prefix="/users")


@users_router.post(
    "/sync",
    summary="Sync user data",
    responses={
        status.HTTP_409_CONFLICT: {"description": "User has more than one role"},
    },
)
async def sync_handler(
    auth: UserAuth,
    controller: UsersController = Depends(),
) -> None:
    await controller.sync_user_roles(auth)


@users_router.get(
    "",
    summary="Search users",
)
async def search_users_handler(
    query: str | None = Query(default=None, description="Search string"),
    offset: int = Query(default=0, description="Pagination offset", ge=0),
    limit: int = Query(default=20, description="Pagination limit", le=50, ge=1),
    filter_by_role: Role | None = Query(default=None, alias="role", description="Filter by role"),
    exclude_me: bool = Query(default=True, description="Exclude current user from the response data"),
    controller: UsersController = Depends(),
    auth: AuthPayload = Depends(supervisor_required),
) -> PaginatedResponse[UserData]:
    users, count = await controller.search_users(
        exclude_user_id=auth.id if exclude_me else None,
        query=query,
        filter_by_role=filter_by_role,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(count=count, data=users)


@users_router.get(
    "/multi",
    summary="Get multiple users by ids",
)
async def get_users_by_ids(
    user_ids: CommaSeparatedNumbers[int] = Query(...),
    controller: UsersController = Depends(),
) -> list[UserData]:
    if len(user_ids) > 100:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Maximum number of users to get is 100",
        )

    return await controller.get_users_by_ids(user_ids)


@users_router.get(
    "/{user_id}",
    summary="Get user by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User with this id does not exist"},
    },
)
async def get_user_by_id(
    user_id: int,
    controller: UsersController = Depends(),
) -> UserData:
    user = await controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "User with this id does not exist",
        )

    return user


@users_router.post(
    "/roles/grant",
    summary="Grant role/ability to the user",
    description="Register user in the system and grant him a given role.",
)
async def grant_handler(
    request: GrantRequest,
    controller: UsersController = Depends(),
    _: AuthPayload = Depends(admin_required),
) -> None:
    if isinstance(request.privilege, Role):
        await controller.grant_role(request.user_id, request.privilege)
        return

    await controller.grant_ability(request.user_id, request.privilege)


@users_router.post(
    "/roles/revoke",
    summary="Revoke role from the user",
    description="Revoke role from the user. If the user has no roles left, he will not be able to access the system",
)
async def revoke_role_handler(
    request: RevokeRequest,
    controller: UsersController = Depends(),
    _: AuthPayload = Depends(admin_required),
) -> None:
    await controller.revoke_role(request.user_id, request.role)
