from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from src.api.http.serializers.push_notifications import (
    DeviceAliveRequest,
    RecoverDeviceIdRequest,
    RecoverDeviceIdResponse,
    SubscribeRequest,
    SubscribeResponse,
    UnsubscribeRequest,
)
from src.controllers.push_notifications import PushNotificationsController
from src.entities.push_notifications import PushClientCredentials
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import auth_required

push_notifications_router = APIRouter(prefix="/notifications/push")


@push_notifications_router.get(
    "/public_key",
    summary="Get public key",
    response_model=None,
    response_class=PlainTextResponse,
)
async def get_public_key_handler(
    controller: PushNotificationsController = Depends(),
    _: AuthPayload = Depends(auth_required),
) -> PlainTextResponse:
    return PlainTextResponse(controller.get_public_key())


@push_notifications_router.post(
    "/alive",
    summary="Indicate that the device and session is alive",
    response_model=None,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Conflict: device is linked to another user"},
    },
)
async def alive_handler(
    request: DeviceAliveRequest,
    controller: PushNotificationsController = Depends(),
    user: AuthPayload = Depends(auth_required),
) -> None:
    await controller.on_device_alive(user_id=user.id, device_id=request.device_id)


@push_notifications_router.post(
    "/recover_device_id",
    summary="Recover device id by endpoint",
    response_model=RecoverDeviceIdResponse,
    responses={status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Subscription not found"}},
)
async def recover_device_id_handler(
    request: RecoverDeviceIdRequest,
    controller: PushNotificationsController = Depends(),
    user: AuthPayload = Depends(auth_required),
) -> RecoverDeviceIdResponse:
    device_id = await controller.recover_device_id(user_id=user.id, endpoint=request.endpoint)
    return RecoverDeviceIdResponse(device_id=device_id)


@push_notifications_router.post(
    "/subscribe",
    summary="Add subscription for push notifications",
    response_model=None,
    responses={status.HTTP_409_CONFLICT: {"description": "Subscription already exists"}},
)
async def add_subscribtion_handler(
    request: SubscribeRequest,
    controller: PushNotificationsController = Depends(),
    user: AuthPayload = Depends(auth_required),
) -> SubscribeResponse:
    push_cfg = await controller.add_subscription(
        user_id=user.id,
        credentials=PushClientCredentials(
            endpoint=request.endpoint,
            keys=request.keys.dict(),
        ),
    )
    return SubscribeResponse(device_id=push_cfg.device_id)


@push_notifications_router.post(
    "/unsubscribe",
    summary="Remove subscription for push notifications",
    response_model=None,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Subscription not found"},
    },
)
async def remove_subscription_handler(
    request: UnsubscribeRequest,
    controller: PushNotificationsController = Depends(),
) -> None:
    await controller.remove_subscriptions(device_id=request.device_id)
