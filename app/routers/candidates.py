from typing import List, Dict

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas.candidates import CandidateShortData
from app.schemas.hh_request import SearchingUrl, ContactUpdateData
from app.schemas.hh_response import CandidateData
from app.services.candidates import Candidates, Candidate
from app.services.g3_api import G3Candidates

candidates_router = APIRouter()


@candidates_router.post("/add_searching_url", summary="Добавление ссылки внутрь сервиса.", tags=["Работа с ссылками"])
async def add_searching_url(url_data: SearchingUrl):
    """Добавление ссылки внутрь сервиса."""

    status = await G3Candidates.insert_url_in_board(url_data=url_data)
    return status


@candidates_router.post(
    "/candidates", summary="Отправка поисковых ссылок на API Headhunter.", tags=["Запросы к HH_API"]
)
async def run_searching_url(urls: List[SearchingUrl], session: AsyncSession = Depends(get_db_session)) -> List[CandidateShortData]:
    """Отправка поисковых ссылок на API Headhunter."""

    candidates = await Candidates(session).process_with_urls(urls)
    # result = await G3Candidates.insert_candidate_in_board(candidates)
    return candidates


@candidates_router.post(
    "/candidate",
    summary="Запрос на получение контактной информации на API Headhunter.",
    tags=["Запросы к HH_API"],
)
async def run_contact_url(contact_data: SearchingUrl, session: AsyncSession = Depends(get_db_session)):
    """Запрос на получение контактной информации на API Headhunter."""

    result = await Candidate(session).process_with_contact_url(contact_data)

    return result
    # return "Пока не работает"
