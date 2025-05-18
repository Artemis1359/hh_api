
from aiohttp import ClientResponse
import logging
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import auth_header, proxies
from app.db.tokens import TokenQuery
from app.exceptions.hh import TokenExpiredError, ExternalApiError
from app.exceptions.token import TokenParamsError, ActionForbidden
from app.schemas.hh_response import TokenData, HHResponseData
from pydantic import ValidationError


class HHResponse:
    """Модуль запросов к HH."""

    def __init__(self, session: AsyncSession):
        self.__proxies = proxies
        self.session = session

    async def send_request(self, url, method, params=None) -> ClientResponse:
        """Метод отправки запросов к API HH."""

        token = await Token(self.session).get()
        headers = auth_header(token)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method, url=url, headers=headers, params=params, proxy=self.__proxies
            ) as response:
                data = await response.json()
                status = response.status
                return HHResponseData(data=data, status=status)


class ResponseChecker:
    """Модуль проверки запросов."""

    @staticmethod
    async def check_response(resource_type: str, response: HHResponseData) -> HHResponseData:
        """Проверка запросов к HeadHunter на статус-код."""

        status_code = response.status
        if status_code == 200:
            return response

        response_json = response.data
        request_id = response_json.get("request_id")
        errors = response_json.get("errors")
        if errors:
            text = f"hh_{resource_type}_{request_id}_{status_code}:"
            if status_code == 400 and resource_type == "candidates":
                text = f"hh_candidates_{request_id}_400:"
            elif status_code == 404 and resource_type == "candidate":
                text = f"hh_candidate_{request_id}_404:"
            elif status_code == 429 and resource_type == "candidate":
                text = f"hh_candidate_{request_id}_429:"
            elif status_code == 403:
                description = response_json.get("description")
                oauth_error = response_json.get("oauth_error")
                logging.error(
                    f"hh_{resource_type}_403_{request_id}: description - {description}, oauth_error - {oauth_error}"
                )
                text = f"hh_{resource_type}_{request_id}_403:"
                if oauth_error == "token-expired":
                    raise TokenExpiredError("Срок действия токена истек")
            for error in errors:
                logging.error(f"{text} {error}")
            raise ExternalApiError(f"Ошибка {resource_type}_{status_code} по заявке {request_id}")
        else:
            logging.error(f"hh_{resource_type}_{request_id}_{status_code}: {response_json}")
            raise ExternalApiError(f"Ошибка {resource_type}_{status_code} по заявке {request_id}")

    @staticmethod
    async def check_token_response(response: HHResponseData) -> HHResponseData:
        """Проверка запросов к токену HeadHunter на статус-код."""

        status_code = response.status
        if status_code == 200:
            return response

        response_json = response.data
        if status_code == 400:
            error = response_json.get("error")
            error_description = response_json.get("error_description")
            logging.error(f"hh_token_{status_code}: {error}  {error_description}")
            raise TokenParamsError(f"Ошибка обновления токена")
        elif status_code == 403:
            description = response_json.get("description")
            oauth_error = response_json.get("oauth_error")
            request_id = response_json.get("request_id")
            errors = response_json.get("errors")
            logging.error(f"hh_token_403_{request_id}: description - {description}, oauth_error - {oauth_error}")
            for error in errors:
                logging.error(f"hh_token_403_{request_id}: {error}")
            raise ActionForbidden(f"Ошибка обновления токена")
        else:
            logging.error(f"hh_token_{status_code}: {response_json}")
            raise ExternalApiError(f"Ошибка обновления токена")


class Token:
    """Модуль работы с токенами."""

    def __init__(self, session: AsyncSession):
        self.url = "https://hh.ru/oauth/token"
        self.session = session


    async def get(self) -> str:
        """Метод для получения токена из бд."""

        token = await TokenQuery(self.session).get_token()
        return token

    async def update(self):
        """Метод для обновления пары access, refresh токенов."""

        refresh_token = TokenQuery(self.session).get_refresh_token()
        params = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        response = await HHResponse().send_request(url=self.url, method="POST", params=params)
        checked_response = await ResponseChecker.check_token_response(response)
        try:
            tokens = TokenData(**checked_response.data)
            await TokenQuery(self.session).insert_new_tokens(tokens)
        except ValidationError as e:
            logging.error(f"hh_token: {e}")
            raise e
