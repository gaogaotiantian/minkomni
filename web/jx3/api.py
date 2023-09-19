import pydantic
from fastapi import APIRouter, Request

from .data_holder import data_holder
from .models import GroupUpdateRequest
from ..util import local_file
from ..util.iplimiter import iplimiter

jx3_router = APIRouter()


@jx3_router.post("/api/group")
@iplimiter(10)
async def add_group(request: Request):
    try:
        data = GroupUpdateRequest(**(await request.json()))
    except pydantic.ValidationError:
        return {"success": False, "msg": "Invalid input"}
    if data_holder.add_group(data):
        return {"success": True, "data": data_holder.get_data()}
    return {"success": False, "msg": "Invalid input"}

@jx3_router.get("/api/group")
async def get_group():
    data = data_holder.get_data()
    return {"success": True, "data": data}

@jx3_router.get("/group_avoid")
@jx3_router.get("/group_avoid.html")
async def group_avoid():
    return local_file("group_avoid.html")
