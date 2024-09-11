from pydantic import BaseModel, Field, SecretStr


class AuthSettings(BaseModel):
    host: str
    aud: str
    priv_key: SecretStr
    request_timeout: float
    token_leeway: int
    extended_token_leeway: int | None = Field(
        default=None,
        description="Extended leeway for token validation, for file uploads",
    )
    verify_signature: bool = Field(
        default=True,
        description="Auth token signature verification. Disable only for testing in local environment",
    )
