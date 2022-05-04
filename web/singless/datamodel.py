from curses.ascii import isdigit
import hashlib
from pydantic import BaseModel, validator

class ApplicantRequest(BaseModel):
    bid: str
    url: str
    pin: str

    @validator("bid")
    def bid_check(cls, v):
        if not 1 <= len(v) <= 11:
            raise ValueError("bid length incorrect")
        if not v.isdigit():
            raise ValueError("bid value invalid")
        return v

    @validator("url")
    def url_check(cls, v):
        if not 1 <= len(v) <= 150:
            raise ValueError("url length too long")
        return v

    @validator("pin")
    def pin_check(cls, v):
        if not 1 <= len(v) <= 150:
            raise ValueError("pin length too long")
        return v

    def get_hash(self):
        return hashlib.sha256((self.bid + self.pin).encode("utf-8")).hexdigest()


class LikeRequest(BaseModel):
    bid: str
    like: str
    pin: str

    @validator("like")
    def like_check(cls, v):
        if not 1 <= len(v) <= 5:
            raise ValueError("like format incorrect")
        if not v.isdigit():
            raise ValueError("like format incorrect")
        return v

    def get_hash(self):
        return hashlib.sha256((self.bid + self.pin).encode("utf-8")).hexdigest()
