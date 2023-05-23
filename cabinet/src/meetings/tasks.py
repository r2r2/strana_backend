from datetime import datetime
from typing import Any

from common import amocrm
from common.kontur_talk.kontur_talk import KonturTalkAPI
from config import celery
from src.meetings import repos as meeting_repos, use_cases


@celery.app.task
async def create_kontur_talk_room_task(date: datetime, meeting_id: int):
    kounter_talk_api = KonturTalkAPI(meeting_repo=meeting_repos.MeetingRepo)
    resources: dict[str, Any] = dict(
        kounter_talk_api=kounter_talk_api,
        meeting_repo=meeting_repos.MeetingRepo,
        amocrm_class=amocrm.AmoCRM,
    )
    create_meeting: use_cases.CreateRoomTaskCase = use_cases.CreateRoomTaskCase(**resources)
    await create_meeting(date, meeting_id)


@celery.app.task
async def open_kontur_talk_room_task(room_name: str):
    await KonturTalkAPI().open_room(room_name)
