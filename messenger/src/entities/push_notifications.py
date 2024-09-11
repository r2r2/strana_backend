from dataclasses import dataclass


@dataclass
class PushClientCredentials:
    endpoint: str
    keys: dict[str, str]
