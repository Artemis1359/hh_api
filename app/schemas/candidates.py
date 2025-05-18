from typing import Optional

from pydantic import BaseModel

from app.schemas import strN, intN
from app.schemas.hh_response import Salary, CandidateData, CandidateDataContact


class CandidateShortData(BaseModel):
    fullname: strN = None
    title: strN = None
    age: intN = None
    salary: Optional[Salary] = None
    owner_id: str
    url: str
    resume_id: str
    board_id: str

    @classmethod
    def from_model_candidate_data(cls, candidate: CandidateData, board_id: str):
        try:
            fullname = candidate.last_name + candidate.first_name + candidate.middle_name
        except TypeError:
            fullname = None
        return cls(
            fullname=fullname,
            title=candidate.title,
            age=candidate.age,
            salary_amount=candidate.salary.amount if candidate.salary else None,
            salary_currency=candidate.salary.currency if candidate.salary else None,
            owner_id=candidate.owner.id,
            url=candidate.alternate_url,
            resume_id=candidate.id,
            board_id=board_id,
        )

    @classmethod
    def from_model_contact_candidate_data(cls, candidate: CandidateDataContact, board_id: str):
        try:
            fullname = candidate.last_name + candidate.first_name + candidate.middle_name
        except TypeError:
            fullname = None
        return cls(
            fullname=fullname,
            title=candidate.title,
            age=candidate.age,
            salary_amount=candidate.salary.amount if candidate.salary else None,
            salary_currency=candidate.salary.currency if candidate.salary else None,
            owner_id=candidate.owner.id,
            url=candidate.alternate_url,
            resume_id=candidate.id,
            board_id=board_id,
        )
