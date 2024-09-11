from enum import auto, unique

from src.core.common import StringEnum


@unique
class ServiceType(StringEnum):
    HTTP_SERVER = auto()
    WS_SERVER = auto()
    JOBS = auto()
    WORKER = auto()
    UPDATES_STREAMER = auto()
    PUSH_SENDER = auto()


SERVICES = {
    ServiceType.HTTP_SERVER: "src.entrypoints.services.http_server:entrypoint",
    ServiceType.WS_SERVER: "src.entrypoints.services.ws_server:entrypoint",
    ServiceType.JOBS: "src.entrypoints.services.jobs:entrypoint",
    ServiceType.WORKER: "src.entrypoints.services.worker:entrypoint",
    ServiceType.UPDATES_STREAMER: "src.entrypoints.services.updates_streamer:entrypoint",
    ServiceType.PUSH_SENDER: "src.entrypoints.services.push_sender:entrypoint",
}
