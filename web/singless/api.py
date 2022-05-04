from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import db
import os
import pydantic

from ..util.iplimiter import iplimiter

from .datamodel import ApplicantRequest, LikeRequest

file_dir = os.path.dirname(__file__)
templates = Jinja2Templates(
    directory=os.path.join(file_dir, "templates")
)
singlessAPI = APIRouter()


@singlessAPI.post("/api/applicant")
@iplimiter(30)
async def applicant(request: Request):
    try:
        data = ApplicantRequest(**(await request.json()))
    except pydantic.ValidationError:
        return {"success": False, "msg": "Invalid input"}

    ref = db.reference(f"/singless/applicants/{data.bid}")
    curr = ref.get()
    if curr is not None and curr["pin"] != data.get_hash():
        return {"success": False, "msg": "incorrect PIN"}

    ref.set({
        "bid": data.bid,
        "url": data.url,
        "pin": data.get_hash()
    })

    return {"success": True, "msg": "提交成功！"}


@singlessAPI.post("/api/like")
@iplimiter(5)
async def like(request: Request):
    try:
        data = LikeRequest(**(await request.json()))
    except pydantic.ValidationError:
        return {"success": False, "msg": "Invalid input"}

    applicant_ref = db.reference(f"/singless/applicants/{data.bid}")
    curr = applicant_ref.get()
    like_ref = db.reference(f"/singless/like/{data.like}")
    if curr is None or curr["pin"] != data.get_hash():
        return {"success": False, "msg": "Invalid user or incorrect PIN"}

    if curr.get("like", None):
        if curr["like"] == data.like:
            return {"success": True, "msg": "提交成功！"}
        elif curr["like"] != "0":
            unlike_ref = db.reference(f"/singless/like/{curr['like']}/{data.bid}")
            if unlike_ref.get():
                unlike_ref.delete()

    applicant_ref.update({
        "like": data.like
    })

    if data.like != "0":
        like_ref.update({
            f"{data.bid}": curr["url"]
        })


    return {"success": True, "msg": "提交成功！"}


@singlessAPI.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@singlessAPI.get("/like", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("like.html", {"request": request})
