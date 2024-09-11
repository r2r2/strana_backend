from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.api.http.serializers.chats import (
    ChatResponse,
    ChatUnreadCountersResponse,
    CreateChatRequest,
    CreateChatResponse,
    UnreadCountResponse,
)
from src.api.http.serializers.users import ResponseWithUserData
from src.constants import INT32_MAX
from src.controllers.chats import ChatsController
from src.controllers.unread_counters import CountersController
from src.controllers.user_data import UserDataAdapter
from src.entities.matches import ChatType
from src.entities.messages import MessageDTO
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import auth_required, supervisor_required

chats_router = APIRouter(prefix="/chats")


@chats_router.get(
    "",
    summary="Get all chats",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_all_chats(
    match_id: int | None = Query(default=None, ge=1, le=INT32_MAX),
    limit: int = Query(default=20, le=50, ge=1),
    offset: int = Query(default=0, ge=0),
    controller: ChatsController = Depends(),
    user: AuthPayload = Depends(auth_required),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[list[ChatResponse]]:
    chat_type = ChatType.PERSONAL if not match_id else None

    return await user_data_adapter.enrich_response(
        response=await controller.search_chats(
            user=user,
            chat_type=chat_type,
            match_id=match_id,
            limit=limit,
            offset=offset,
        ),
    )


@chats_router.get(
    "/unread_count",
    summary="Get count of unread messages for all chats",
    deprecated=True,
)
async def get_unread_count(
    user: AuthPayload = Depends(auth_required),
    controller: ChatsController = Depends(),
) -> UnreadCountResponse:
    return await controller.get_unread_count(user=user)


@chats_router.get(
    "/unread_counters",
    summary="Get counters of unread messages for all chats",
)
async def get_unread_counters(
    user: AuthPayload = Depends(auth_required),
    controller: CountersController = Depends(),
) -> ChatUnreadCountersResponse:
    return await controller.get_unread_counters(user)


@chats_router.get(
    "/{chat_id}",
    summary="Get chat",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
    },
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_chat(
    chat_id: int,
    user: AuthPayload = Depends(auth_required),
    controller: ChatsController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[ChatResponse]:
    return await user_data_adapter.enrich_response(
        response=await controller.get_chat(chat_id=chat_id, user=user),
    )


@chats_router.post(
    "",
    summary="Create new chat",
    response_model=CreateChatResponse,
    responses={
        status.HTTP_409_CONFLICT: {"model": CreateChatResponse, "description": "Chat already exists"},
    },
)
async def create_chat(
    request: CreateChatRequest,
    user: AuthPayload = Depends(auth_required),
    controller: ChatsController = Depends(),
) -> JSONResponse:
    chat_id, is_new = await controller.create_chat(user=user, target_user_id=request.target_user_id)
    return JSONResponse(
        content={"chat_id": chat_id},
        status_code=status.HTTP_200_OK if is_new else status.HTTP_409_CONFLICT,
    )


@chats_router.get(
    "/{chat_id}/messages",
    summary="Get chat messages",
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_chat_messages(
    chat_id: int,
    from_message_id: int | None = Query(
        default=None,
        description="ID of the message from which to start the search (exclusive)",
    ),
    limit: int = Query(default=30, description="Pagination limit", le=100, ge=1),
    backwards: bool = Query(default=False, description="Search backwards (to older messages)"),
    controller: ChatsController = Depends(),
    user: AuthPayload = Depends(auth_required),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[list[MessageDTO]]:
    return await user_data_adapter.enrich_response(
        response=await controller.get_chat_messages(
            chat_id=chat_id,
            from_message_id=from_message_id,
            limit=limit,
            backwards=backwards,
            user=user,
        ),
    )


@chats_router.post(
    "/{chat_id}/join",
    summary="Join the chat",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Action is not permitted"},
        status.HTTP_409_CONFLICT: {"description": "The user is already a member of the chat room"},
    },
)
async def join_chat(
    chat_id: int,
    user: AuthPayload = Depends(auth_required),
    controller: ChatsController = Depends(),
) -> None:
    await controller.join_chat(chat_id=chat_id, user=user)


@chats_router.post(
    "/{chat_id}/leave",
    summary="Leave the chat",
    description=("The user can leave only general chats and specific chats in which he is a secondary member"),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Action is not permitted"},
        status.HTTP_409_CONFLICT: {"description": "The user is not a member of the chat room"},
    },
)
async def leave_chat(
    chat_id: int,
    user: AuthPayload = Depends(auth_required),
    controller: ChatsController = Depends(),
) -> None:
    await controller.leave_chat(chat_id=chat_id, user=user)


@chats_router.post(
    "/{chat_id}/close",
    summary="Close the chat",
    description="The user can close only NON_SPECIFIC chats if he has the role of the supervisor",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Only non-specific chats can be closed"},
        status.HTTP_409_CONFLICT: {"description": "The chat is already closed"},
    },
)
async def close_chat(
    chat_id: int,
    user: AuthPayload = Depends(supervisor_required),
    controller: ChatsController = Depends(),
) -> None:
    await controller.close_chat(chat_id=chat_id, user=user)


@chats_router.post(
    "/{chat_id}/open",
    summary="Open the chat",
    description="The user can open only opened NON_SPECIFIC chats if he has the role of the supervisor",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Only non-specific chats can be opened"},
        status.HTTP_409_CONFLICT: {"description": "The chat is not closed"},
    },
)
async def open_chat(
    chat_id: int,
    user: AuthPayload = Depends(supervisor_required),
    controller: ChatsController = Depends(),
) -> None:
    await controller.open_chat(chat_id=chat_id, user=user)
