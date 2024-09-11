from fastapi import APIRouter, Depends, Query, status

from src.api.http.serializers.chats import ChatOptionsResponse
from src.api.http.serializers.matches import (
    MatchListResponse,
    MatchResponse,
    StartChatWithScoutRequest,
    StartChatWithScoutResponse,
    parse_match_filters,
)
from src.api.http.serializers.users import ResponseWithUserData
from src.controllers.matches import MatchesController
from src.controllers.user_data import UserDataAdapter
from src.entities.matches import MatchFilters
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import auth_required

matches_router = APIRouter(prefix="/matches")


@matches_router.get(
    "",
    summary="Get matches",
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_matches(
    offset: int = Query(default=0, description="Pagination offset", ge=0),
    limit: int = Query(default=20, description="Pagination limit", le=50, ge=1),
    filters: MatchFilters = Depends(parse_match_filters),
    user: AuthPayload = Depends(auth_required),
    controller: MatchesController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[list[MatchResponse]]:
    return await user_data_adapter.enrich_response(
        await controller.get_matches(
            user=user,
            filters=filters,
            limit=limit,
            offset=offset,
        ),
    )


@matches_router.get(
    "/list",
    summary="Get matches",
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_matches_list(
    offset: int = Query(default=0, description="Pagination offset", ge=0),
    limit: int = Query(default=20, description="Pagination limit", le=50, ge=1),
    filters: MatchFilters = Depends(parse_match_filters),
    user: AuthPayload = Depends(auth_required),
    controller: MatchesController = Depends(),
) -> list[MatchListResponse]:
    return await controller.get_matches_list(
        user=user,
        filters=filters,
        limit=limit,
        offset=offset,
    )


@matches_router.get(
    "/{match_id}",
    summary="Get match by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Match not found or not accessible"},
    },
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_match(
    match_id: int,
    index: bool | None = Query(
        default=None, description="Whether to retrieve match info from SL if it is not found in DB"
    ),
    user: AuthPayload = Depends(auth_required),
    controller: MatchesController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[MatchResponse]:
    return await user_data_adapter.enrich_response(
        await controller.get_match(user=user, match_id=match_id, try_index=index),
    )


@matches_router.post(
    "/{match_id}/chat",
    summary="Start a new chat for the match",
    description="Action is only available to bookmakers if they want to start a chat with a scout",
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Only a bookmaker can start a chat for a match"},
    },
)
async def start_chat(
    match_id: int,
    request: StartChatWithScoutRequest,
    user: AuthPayload = Depends(auth_required),
    controller: MatchesController = Depends(),
) -> StartChatWithScoutResponse:
    return await controller.start_chat(
        user=user,
        match_id=match_id,
        scout_user_id=request.scout_user_id,
    )


@matches_router.get(
    "/{match_id}/options",
    summary="Get options for creating a new chat with a scout",
)
async def get_options(
    match_id: int,
    user: AuthPayload = Depends(auth_required),
    controller: MatchesController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[ChatOptionsResponse]:
    return await user_data_adapter.enrich_response(
        await controller.get_chat_options(
            user=user,
            match_id=match_id,
        ),
    )
