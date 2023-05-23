from typing import Type, Callable, Coroutine, Any, Optional

from aiohttp import ClientSession, TCPConnector

from config import kontur_talk_config, maintenance_settings
from src.meetings.repos import MeetingRepo, Meeting
from .exceptions import BaseKonturTalkRequestException
from ..requests import CommonRequest, CommonResponse


class KonturTalkAPI:
    """
    Интеграция Kontur Talk
    """

    _auth_headers: dict[str, str] = {"X-Auth-Token": kontur_talk_config.get("secret")}

    def __init__(self, meeting_repo: Optional[Type[MeetingRepo]] = None):
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()
        self._url: str = f"https://{kontur_talk_config['space']}.ktalk.ru/"
        self._url_api: str = self._url + "api/"
        self._request_class: Type[CommonRequest] = CommonRequest
        # Need this if you wanna only CREATE room
        if meeting_repo:
            self.meeting_repo: MeetingRepo = meeting_repo()

    async def __aenter__(self) -> 'KonturTalkAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            await self._session.close()

    def _put_options(self, data: dict[str, Any], _query: dict[str, Any], endpoint: str) -> dict[str, Any]:
        return dict(
            method="PUT",
            json=data,
            query=_query,
            url=self._url_api + endpoint,
            session=self._session,
            headers=self._auth_headers,
            timeout=300,
        )

    async def _request_put(self, data: dict[str, Any], query: dict[str, Any], endpoint: str) -> CommonResponse:
        request_options: dict[str, Any] = self._put_options(data, query, endpoint)
        request_put: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_put()
        return response

    @staticmethod
    def _payload_put_room(
            title: str = "",
            description: str = "",
            moderator_keys: Optional[list] = None,
            enable_session_halls: bool = True,
            enable_lobby: bool = False,
            audio_policy: str = "1",
            video_policy: str = "none",
            screen_share_policy: str = "none",
            max_video_quality: int = 0,
            allow_anonymous: bool = True,
    ) -> dict:
        return dict(
            title=title,
            description=description,
            moderatorKeys=moderator_keys or [],
            enableSessionHalls=enable_session_halls,
            enableLobby=enable_lobby,
            audioPolicy=audio_policy,
            videoPolicy=video_policy,
            screenSharePolicy=screen_share_policy,
            maxVideoQuality=max_video_quality,
            allowAnonymous=allow_anonymous
        )

    async def create_room(self, room_name: str, meeting_id: int) -> str:
        data = self._payload_put_room(enable_lobby=True)
        response: CommonResponse = await self._request_put(data=data, query=dict(), endpoint=f"rooms/{room_name}")
        if response.status != 200:
            raise BaseKonturTalkRequestException()
        meeting: Meeting = await self.meeting_repo.retrieve(filters=dict(id=meeting_id))
        update_data = dict(meeting_link=self._url + room_name)
        await self.meeting_repo.update(model=meeting, data=update_data)
        return f"{self._url}{room_name}"

    async def open_room(self, room_name: str) -> str:
        data = self._payload_put_room()
        response: CommonResponse = await self._request_put(data=data, query=dict(), endpoint=f"rooms/{room_name}")
        if response.status != 200:
            raise BaseKonturTalkRequestException()
        return f"{self._url}{room_name}"
