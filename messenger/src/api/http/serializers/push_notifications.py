from pydantic import BaseModel, Field


class ClientKeyPair(BaseModel):
    auth: str
    p256dh: str


class DeviceAliveRequest(BaseModel):
    device_id: str = Field(..., max_length=100, min_length=1)


class SubscribeRequest(BaseModel):
    endpoint: str
    keys: ClientKeyPair


class SubscribeResponse(BaseModel):
    device_id: str


class UnsubscribeRequest(BaseModel):
    device_id: str = Field(..., max_length=100, min_length=1)


class RecoverDeviceIdRequest(BaseModel):
    endpoint: str


class RecoverDeviceIdResponse(BaseModel):
    device_id: str
