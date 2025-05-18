from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse, parse_qsl, unquote

from app.exceptions.hh import RelocationWithoutAreaError
from app.schemas.candidates import CandidateShortData
from app.schemas.hh_response import CandidateData, CandidateDataList, CandidateDataContact


class Transformer(ABC):

    @staticmethod
    @abstractmethod
    def transform(item, board_id: None):
        pass


class CandidateContactTransformer(Transformer):

    @staticmethod
    def transform(candidate: CandidateDataContact, board_id: str) -> CandidateShortData:
        """Привидение данных в формат CandidateShortData по контактным данным."""

        transformed_candidate = CandidateShortData.from_model_contact_candidate_data(candidate, board_id=board_id)

        return transformed_candidate


class CandidateTransformer(Transformer):
    """Привидение данных в формат CandidateShortData в цикле."""

    @staticmethod
    def transform(candidates: List[CandidateData], board_id: str) -> List[CandidateShortData]:
        transformed = []
        for candidate in candidates:
            transformed_candidate = CandidateShortData.from_model_candidate_data(candidate, board_id=board_id)
            transformed.append(transformed_candidate)
        return transformed


class SearchingUrlTransformer(Transformer):

    @staticmethod
    def transform(url: str, board_id: None):
        default_period = 7
        parsed_url = urlparse(url)
        query_params = parse_qsl(unquote(parsed_url.query))
        text = 0
        text_logic = {"logic": 0, "pos": 0, "exp_period": 0, "exp_company_size": 0}
        check_relocation = {}
        transformed = []
        for key, value in query_params:
            if key == "items_on_page":
                transformed.append(("per_page", "100"))
            elif key == "text":
                if value:
                    text += 1
                    transformed.append((key, value.replace("+", "%20")))
            elif key == "logic":
                if text == text_logic[key] + 1:
                    logic_value = "all" if value == "normal" else value
                    transformed.append(("text.logic", logic_value))
            elif key == "search_period":
                try:
                    period = int(value)
                    if period == -1:
                        continue
                    transformed.append(("period", str(min(period, default_period))))
                except ValueError:
                    transformed.append(("period", default_period))
            elif key == "order_by":
                transformed.append((key, "publication_time"))
            elif key in {"age_from", "age_to", "salary_from", "salary_to"}:
                continue
            elif key == "currency_code":
                transformed.append(("currency", value))
            elif key == "pos":
                if text == text_logic[key] + 1:
                    mapping = {
                        "full_text": "everywhere",
                        "position": "title",
                        "keywords": "skills",
                        "workplaces": "experience",
                        "workplace_position": "experience_position",
                        "workplace_description": "experience_description",
                        "workplace_organization": "experience_company",
                    }
                    mapped_value = mapping.get(value)
                    transformed.append(("text.field", mapped_value))
            elif key == "exp_period":
                if text == text_logic[key] + 1:
                    transformed.append(("text.period", value))
            elif key == "exp_company_size":
                if text == text_logic[key] + 1:
                    transformed.append(("text.company_size", value))
            elif key == "language":
                lang, level = value.split(".", 1)
                transformed.append(("language", lang))
                transformed.append(("language_level", level))
            elif key == "relocation" or key == "area":
                check_relocation[key] = 1
                transformed.append((key, value))
            elif key == "education_level":
                transformed.append(("education_levels", value))
            else:
                transformed.append((key, value))
        if check_relocation.get("relocation", 0) > check_relocation.get("area", 0):
            raise RelocationWithoutAreaError("Укажите регион или уберите параметр релокации.")
        search_url = "https://api.hh.ru/resumes?" + "&".join(f"{k}={v}" for k, v in transformed if v)
        return search_url


# searching_url = Transformer.searching_url(url='''https://hh.ru/search/resume?logic=normal&logic=normal&pos=full_text&pos=full_text&exp_period=all_time&exp_period=all_time&order_by=relevance&search_period=0&items_on_page=50&hhtmFrom=resume_search_form&area=113&citizenship=113&employment=full&experience=noExperience&education_level=bachelor&filter_exp_period=all_time&job_search_status=active_search&job_search_status=accepted_job_offer&label=only_with_gender&professional_role=8&relocation=living&schedule=fullDay&skill=3864&skill=845&text=&text=&gender=female''')
# candidate = Candidates().some_func(url=searching_url)
# print(len(candidate['items']))
# print([candidate.get('education').get('level') for candidate in candidate['items']])
