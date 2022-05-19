import re

from pydantic import BaseModel, validator


iq_regex = re.compile(r"[SABCD][+-]?")


class IQRequest(BaseModel):
    iq: str

    @validator("iq")
    def iq_check(cls, v: str):
        v = v.upper()
        if iq_regex.fullmatch(v) is None:
            raise ValueError("IQ invalid")
        return v

    @staticmethod
    def iq_to_number(iq):
        num = {
            "S": 100,
            "A": 90,
            "B": 80,
            "C": 70,
            "D": 60
        }[iq[0]]
        num += iq.count("+")
        num -= iq.count("-")
        return num


class IQUpdateRequest(IQRequest):
    celebrity_name: str


class IQDeleteRequest(BaseModel):
    celebrity_name: str


class IQCommentUpdateRequest(BaseModel):
    celebrity_name: str
    comment_type: str
    comment_score: int
    comment: str


class IQCommentDeleteRequest(BaseModel):
    celebrity_name: str
    comment_id: str
