from google.protobuf.message import Message as ProtobufMessage

from src.entities.messages import MAX_MESSAGE_LENGTH
from src.exceptions import MessageValidationError


async def validate_message(message_command: ProtobufMessage) -> None:
    content = message_command.content  # type: ignore
    content_type = content.WhichOneof("content")
    match content_type:
        case "text":
            if len(content.text.text) > MAX_MESSAGE_LENGTH:
                raise MessageValidationError(f"Maximum message length - {MAX_MESSAGE_LENGTH} characters")

        case _:
            raise MessageValidationError(f"Unsupported message content type: {content_type}")
