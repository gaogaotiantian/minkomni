from datetime import datetime

from pydantic import BaseModel, validator

class GroupUpdateRequest(BaseModel):
    group: str
    description: str
    date: str

    @validator("date")
    @classmethod
    def date_format(cls, v: str):
        v = v.strip().replace("-", "/")
        if not v:
            return datetime.now().strftime("%y/%m/%d")
        for format in ["%y/%m/%d", "%Y/%m/%d"]:
            try:
                d = datetime.strptime(v, format)
            except ValueError:
                pass
            else:
                return d.strftime("%y/%m/%d")
        raise ValueError("Date format invalid")
