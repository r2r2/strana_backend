from pydantic import BaseModel


class SLMatchScoutChangePayload(BaseModel):
    translation_id: int
    sport_id: int
    event_id: int
    state_id: int
    scout_id: int | None
    changed_at: int
