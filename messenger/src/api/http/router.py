from fastapi import APIRouter

from src.api.http.chats import chats_router
from src.api.http.common import common_router
from src.api.http.compound import compound_router
from src.api.http.file_uploads import file_uploads_router
from src.api.http.matches import matches_router
from src.api.http.messages import messages_router
from src.api.http.push_notifications import push_notifications_router
from src.api.http.tickets import tickets_router
from src.api.http.users import users_router

http_api_router = APIRouter(prefix="/api/v1")
http_api_router.include_router(chats_router, tags=["Chats"])
http_api_router.include_router(matches_router, tags=["Matches"])
http_api_router.include_router(common_router, tags=["Common"])
http_api_router.include_router(tickets_router, tags=["Tickets"])
http_api_router.include_router(users_router, tags=["Users"])
http_api_router.include_router(file_uploads_router, tags=["File uploads"])
http_api_router.include_router(compound_router, tags=["Compound operations"])
http_api_router.include_router(push_notifications_router, tags=["Push notifications"])
http_api_router.include_router(messages_router, tags=["Messages"])
