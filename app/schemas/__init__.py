from pydantic import BaseModel
from typing import Optional


strN = Optional[str]
intN = Optional[int]
boolN = Optional[bool]


class IdStr(BaseModel):
    id: str


class IdNameStr(IdStr):
    name: str


class UrlStr(BaseModel):
    url: str


class IdNoneNameStr(BaseModel):
    id: strN = None
    name: str
