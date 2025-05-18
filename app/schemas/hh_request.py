from pydantic import BaseModel


class SearchingUrl(BaseModel):
    board_id: str
    url: str

class ContactUpdateData(BaseModel):
    board_id: str
    resume_id: str
