from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status

from src.api.http.serializers.messages import UnreadMessagesResponse, UpdateMessageRequest
from src.constants import INT32_MAX
from src.controllers.messages import MessagesController
from src.entities.messages import MessageDTO
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import auth_required
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import Message

messages_router = APIRouter(prefix="/messages")


async def own_message_required(
    message_id: int = Path(..., ge=1, le=INT32_MAX),
    storage: StorageProtocol = Depends(inject_storage),
    user: AuthPayload = Depends(auth_required),
) -> Message:
    message = await storage.messages.get_message_by_id(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    if user.id != message.sender_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this message",
        )

    return message


@messages_router.patch(
    "/{message_id}",
    summary="Update message",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Message not found"},
    },
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def update_message(
    message: Message = Depends(own_message_required),
    payload: UpdateMessageRequest = Body(...),
    controller: MessagesController = Depends(),
) -> MessageDTO:
    return await controller.update_message(
        message=message,
        payload=payload,
    )


@messages_router.delete(
    "/{message_id}",
    summary="Delete message",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Message not found"},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message(
    message: Message = Depends(own_message_required),
    controller: MessagesController = Depends(),
) -> None:
    await controller.delete_message(message=message)


@messages_router.get(
    "/unread",
    summary="Get unread messages",
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_unread_messages(
    user: AuthPayload = Depends(auth_required),
    controller: MessagesController = Depends(),
    offset: int = Query(default=0, description="Pagination offset", ge=0),
    limit: int = Query(default=100, description="Pagination limit", ge=1),
) -> UnreadMessagesResponse:
    return await controller.get_unread_messages(
        user=user,
        offset=offset,
        limit=limit,
    )
