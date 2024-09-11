from pydantic import BaseModel


class SLMatchStateUpdatePayload(BaseModel):
    translation_id: int
    state_id: int
    state_changed_at: int
    sport_id: int
    event_id: int | None
