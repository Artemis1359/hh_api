from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text

from app.models.hh_api import Tokens
from app.schemas.hh_response import TokenData


class TokenQuery:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_token(self):
        query = """
                SELECT access_token
                FROM hh_tokens
                ORDER BY id desc
                LIMIT 1;
                """
        result = await self.session.execute(text(query))
        token = result.mappings().first()
        return token.get("access_token")

    async def get_refresh_token(self):

        query = """
                    SELECT refresh_token
                    FROM hh_tokens
                    ORDER BY id desc
                    LIMIT 1
                    """
        result = await self.session.execute(text(query))
        refresh_token = result.mappings().first()
        return refresh_token.get("refresh_token")

    async def insert_new_tokens(self, data: TokenData):

        tokens = Tokens(access_token=data.access_token, refresh_token=data.refresh_token)
        self.session.add(tokens)
        await self.session.commit()
