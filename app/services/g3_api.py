import logging
from typing import List
import requests
from app.schemas.candidates import CandidateShortData
from app.core.config import domain
import aiohttp

from app.schemas.hh_request import SearchingUrl
from app.services.transfromer import SearchingUrlTransformer


class G3Candidates:
    """Модуль взаимодействия с API G3."""

    @staticmethod
    async def insert_candidate_in_board(candidates: List[CandidateShortData]):
        """Метод для вставки данных по кандидату в БД G3."""

        url = domain + "/widgets/apps/by-name/recruitment_test/widgets/by-name/API_WIDGET/run"
        for candidate in candidates:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=dict(candidate)) as response:
                        logging.info(f'hh_candidates: в доску {candidate.board_id} добавлено резюме {candidate.resume_id}')
            except Exception as e:
                logging.error(
                    f'hh_candidates: Возникла ошибка в доске {candidate.board_id} при добавлении резюме {candidate.resume_id}')
                logging.error(f'hh_candidates_error: {e}')
        return {'message': 'Добавление кандидатов прошло успешно'}

    @staticmethod
    async def insert_url_in_board(url_data: SearchingUrl):
        """Метод для вставки ссылки в БД G3."""

        url = domain + ""
        search_url_data = SearchingUrlTransformer.transform(url=url_data.url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=search_url_data) as response:
                    logging.info(f'hh_url: в доску {url.board_id} добавлена ссылка {url.url}')
        except Exception as e:
            logging.error(
                f'hh_urls: Возникла ошибка в доске {url.board_id} при добавлении резюме № {url.url}')
            logging.error(f'hh_urls_error: {e}')
            raise e
        return {'message': 'Добавление ссылки прошло успешно'}