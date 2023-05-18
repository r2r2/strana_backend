from datetime import datetime, timedelta

from common.kontur_talk.kontur_talk import KonturTalkAPI
from config import celery
from src.meetings import repos as meeting_repos


@celery.app.task
async def create_kontur_talk_room_task(date: datetime, meeting_id: int):
    room_name = f"{date.timestamp()}"
    ktalk_api = KonturTalkAPI(meeting_repo=meeting_repos.MeetingRepo)
    await ktalk_api.create_room(room_name, meeting_id)

    _open_kontur_talk_room_task.apply_async((room_name,), eta=(date - timedelta(minutes=5)))


@celery.app.task
async def _open_kontur_talk_room_task(room_name: str):
    await KonturTalkAPI().open_room(room_name)
