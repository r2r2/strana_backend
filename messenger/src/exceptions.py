class BaseError(Exception):
    description: str = "Base exception for service"

    def __init__(self, message: str | None = None) -> None:
        super().__init__()
        if not message:
            message = self.description

        self.message = message


class ClientError(BaseError):
    description = "Error caused by the client"


class ServerError(BaseError):
    description = "Error caused by the server"


class InternalError(ServerError):
    description = "Internal error (сaused by an error in configuration or code)"


class AuthRequiredError(ClientError):
    description = "The user did not provide authentication data"


class InvalidAuthCredentialsError(ClientError):
    description = "Invalid data for authentication"


class InsufficientPrivilegesError(ClientError):
    description = "Action is not permitted for the user"


class ServerShutdownError(BaseError):
    description = "Server is shutting down"


class WebsocketError(BaseError):
    description = "Generic websocket error"


class InvalidMessageReceivedError(ClientError):
    description = "Invalid message was received"


class InvalidMessageTypeError(InvalidMessageReceivedError):
    description = "The obtained data is not in binary form"


class InvalidMessageStructureError(InvalidMessageReceivedError):
    description = "Invalid message structure (protobuf)"


class MessageValidationError(InvalidMessageReceivedError):
    description = "Error when validating the message content"


class NotPermittedError(InsufficientPrivilegesError):
    description = "The action is not permitted to the user"


class ConnectionClosedError(WebsocketError):
    description = "Connection was closed"
