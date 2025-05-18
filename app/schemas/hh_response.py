from typing import Optional, List, Literal, Union, Dict
from pydantic import BaseModel
from app.schemas import boolN, IdNameStr, IdNoneNameStr, IdStr, intN, strN, UrlStr


class Area(IdNameStr):
    url: str


class Certificate(BaseModel):
    achieved_at: str
    owner: strN = None
    title: str
    type: Literal["custom", "microsoft"]
    url: strN = None


class Download(BaseModel):
    pdf: UrlStr
    rtf: UrlStr


class AdditionalEdu(IdNoneNameStr):
    organization: str
    result: strN = None
    year: int


class ElementaryEdu(IdNoneNameStr):
    year: int


class PrimaryEdu(IdNoneNameStr):
    education_level: IdNameStr
    name_id: strN = None
    organization: strN = None
    organization_id: strN = None
    result: strN = None
    result_id: strN = None
    university_acronym: strN = None
    year: int


class Education(BaseModel):
    additional: Optional[List[AdditionalEdu]] = []
    attestation: Optional[List[AdditionalEdu]] = []
    elementary: Optional[List[ElementaryEdu]] = []
    level: IdNameStr
    primary: Optional[List[PrimaryEdu]] = []


class Salary(BaseModel):
    amount: intN = None
    currency: strN = None


class TotalExperience(BaseModel):
    months: intN = None


class Actions(BaseModel):
    download: Download
    download_with_contact: Optional[Download] = None
    get_with_contact: Optional[UrlStr] = None


class Employer(IdNameStr):
    alternate_url: str
    url: str


class Experience(BaseModel):
    area: Optional[Area] = None
    company: strN = None
    company_id: strN = None
    company_url: strN = None
    employer: Optional[Employer] = None
    end: strN = None
    industries: List[IdNameStr] = []
    industry: Optional[IdNameStr] = None
    position: strN = None
    start: str


class Counters(BaseModel):
    total: int


class Comments(UrlStr):
    counters: Counters


class Owner(IdStr):
    comments: Comments


class Photo(BaseModel):
    medium: str
    small: str


class LastNegotiation(BaseModel):
    created_at: str
    employer_state: IdNameStr


class JobSearchStatus(IdNameStr):
    last_change_time: strN = None


class Phone(BaseModel):
    city: str
    country: str
    formatted: str
    number: str


class Contact(BaseModel):
    comment: strN = None
    need_verification: boolN = None
    preferred: boolN = None
    type: IdNameStr
    value: Union[Phone, strN]
    verified: boolN = None


class Language(IdNameStr):
    level: IdNameStr


class Relocation(BaseModel):
    area: List[Area] = []
    district: List[IdNameStr] = []
    type: IdNameStr


class Site(BaseModel):
    url: strN = None
    type: IdNameStr


class Portfolio(BaseModel):
    description: strN = None
    medium: str
    small: str


class CandidateDateTemplate(IdStr):
    alternate_url: str
    title: strN = None
    age: intN = None
    area: Optional[Area] = None
    can_view_full_info: boolN = None
    certificate: List[Certificate] = []
    created_at: str
    download: Download
    education: Education
    first_name: strN = None
    gender: Optional[IdNameStr] = None
    hidden_fields: List[IdNameStr] = []
    last_name: strN = None
    marked: bool = False
    middle_name: strN = None
    platform: IdStr
    salary: Optional[Salary] = None
    total_experience: Optional[TotalExperience] = None
    updated_at: str
    experience: List[Experience] = []
    tags: Optional[List[IdStr]] = None
    actions: Actions
    favorited: bool
    negotiations_history: UrlStr
    owner: Owner
    photo: Optional[Photo] = None
    job_search_status: Optional[JobSearchStatus] = None


class CandidateData(CandidateDateTemplate):

    viewed: boolN = None
    last_negotiation: Optional[LastNegotiation] = None
    url: strN = None


class CandidateDataList(BaseModel):
    items: List[CandidateData] = []
    found: int


class CandidateDataContact(CandidateDateTemplate):
    birth_date: strN = None
    business_trip_readiness: IdNameStr
    citizenship: List[Area] = []
    contact: List[Contact]
    driver_license_types: List[IdStr]
    employments: List[IdNameStr]
    has_vehicle: boolN = None
    language: List[Language]
    professional_roles: List[IdNameStr]
    relocation: Relocation
    schedules: List[IdNameStr]
    site: List[Site] = []
    skill_set: List[str]
    skills: strN = None
    travel_time: IdNameStr
    work_ticket: List[Area]
    portfolio: List[Portfolio]


class TokenData(BaseModel):
    access_token: str
    refresh_token: str

class HHResponseData(BaseModel):
    data: Dict
    status: int
