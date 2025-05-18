import logging
import math
from typing import List, Dict

from fastapi import Depends
from requests import session
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.db.candidates import CandidateQuery
from app.exceptions.hh import TokenExpiredError
from app.schemas.candidates import CandidateShortData
from app.schemas.hh_request import SearchingUrl, ContactUpdateData
from app.schemas.hh_response import CandidateDataList, CandidateData, CandidateDataContact
from app.services.response import HHResponse, ResponseChecker, Token
from app.services.transfromer import CandidateTransformer, CandidateContactTransformer


class BaseCandidate:
    """Базовый модуль работы с кандидатами и запросами к ним."""

    def __init__(self, session: AsyncSession):
        self.resource_type = "base"
        self.session = session

    async def get_data_by_url(self, item):
        """Получаем данные по ссылке."""

        try:
            response = await HHResponse(self.session).send_request(method="GET", url=item)
            response = await ResponseChecker.check_response(resource_type=self.resource_type, response=response)
        except TokenExpiredError:
            await Token(self.session).update()
            response = await HHResponse(self.session).send_request(method="GET", url=item)
        return response

class Candidates(BaseCandidate):
    """Модуль работы с запросом к кандидатам."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.resource_type = "candidates"
        self.per_page = 100

    async def process_with_urls(self, urls: List[SearchingUrl]) -> List[CandidateShortData]:

        # async def process_with_urls(self, urls: List[SearchingUrl]) -> Dict:
        if urls:
            candidates_list = []
            for url in urls:
                pages = await self.__get_actual_pages(url.url)
                candidates = await self.__collect_candidates_per_pages(url, pages)
                candidates_list += candidates
            new_resumes = await Familiar(session=self.session).only_new_resumes(candidates_list)
            return new_resumes

    async def __get_actual_pages(self, url: str) -> int:
        """Узнаем общее количество страниц с людьми в 1 ссылке."""

        limit_url = url.replace("per_page=100", "per_page=1")
        response = await self.__get_data_by_url(url=limit_url)
        try:
            pages = math.ceil(response.found / self.per_page)
        except TypeError:
            logging.error(f"hh_url_error: ошибка в количестве кандидатов {url}")
            pages = 0
        return pages

    async def __collect_candidates_per_pages(self, url: SearchingUrl, pages: int) -> List[CandidateData]:
        candidates_list = []
        for page in range(pages):
            search_url = url.url + f"page={page}"
            candidates = await self.__get_data_by_url(url=search_url)
            transformed_candidates = CandidateTransformer.transform(candidates=candidates.items, board_id=url.board_id)
            candidates_list += transformed_candidates
        return candidates_list

    async def __get_data_by_url(self, url) -> CandidateDataList:
        """Получаем данные по ссылке, включая список кандидатов."""

        response = await super().get_data_by_url(url)
        return CandidateDataList(**response.data)


class Candidate(BaseCandidate):
    """Модуль работы с запросом к контактным данным определенного кандидата."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.resource_type = "candidates"

    async def process_with_contact_url(self, data: SearchingUrl):

        url = 'https://api.hh.ru/resumes/' + data.url.split('/')[-1]
        response = await self.__get_data_by_url(url)
        transformed_candidates = CandidateContactTransformer.transform(candidate=response,
                                                                       board_id=data.board_id)
        return transformed_candidates

    async def __get_data_by_url(self, url) -> CandidateDataContact:
        """Получаем данные по ссылке, включая список кандидатов."""

        response = await super().get_data_by_url(url)

        return CandidateDataContact(**response.data)



class Familiar:
    """Модуль работы с уникальными резюме."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def only_new_resumes(self, resumes: List[CandidateShortData]) -> List[CandidateShortData]:
        """Метод, который отбирает только новые резюме."""

        resume_ids = {resume.resume_id for resume in resumes}
        old_resume_ids = await CandidateQuery(self.session).check_resume_ids(tuple(resume_ids))
        new_resume_ids = resume_ids - old_resume_ids
        new_candidates = [resume for resume in resumes if resume.resume_id in new_resume_ids]
        return new_candidates
