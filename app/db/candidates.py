from typing import List, Set

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session, get_db_session
from sqlalchemy import text, bindparam


class CandidateQuery:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def check_resume_ids(self, resume_ids: tuple) -> Set[str]:
        query = """
                    SELECT id
                    FROM hh_resume_ids
                    WHERE id in :resume_ids
                    """
        result = await self.session.execute(
            text(query).bindparams(bindparam("resume_ids", expanding=True)), {"resume_ids": resume_ids}
        )
        ids = result.mappings().all()
        ids = {resume_id.get("id") for resume_id in ids}
        return ids
