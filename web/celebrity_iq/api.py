from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException

from ..util import local_file
from ..auth import require_admin

from .models import IQUpdateRequest, IQCommentUpdateRequest, IQCommentDeleteRequest, IQDeleteRequest
from .data_holder import data_holder

celebrity_iq_router = APIRouter()


@celebrity_iq_router.put("/api/iq", dependencies=[Depends(require_admin)])
async def add_iq(data: IQUpdateRequest):
    data_holder.update_data(data)
    return {"success": True}


@celebrity_iq_router.post("/api/iq")
async def update_iq(data: IQUpdateRequest):
    data_holder.update_data(data)
    return {"success": True}


@celebrity_iq_router.delete("/api/iq", dependencies=[Depends(require_admin)])
async def delete_iq(data: IQDeleteRequest):
    data_holder.delete_data(data)
    return {"success": True}


@celebrity_iq_router.get("/api/iq")
async def get_iq():
    data = data_holder.get_data()
    return {"success": True, "data": data}


@celebrity_iq_router.post("/api/iq_comment", dependencies=[Depends(require_admin)])
async def add_iq_comment(data: IQCommentUpdateRequest):
    if not data_holder.add_comment(data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such celebrity"
        )
    return {"success": True}


@celebrity_iq_router.delete("/api/iq_comment", dependencies=[Depends(require_admin)])
async def delete_iq_comment(data: IQCommentDeleteRequest):
    if not data_holder.delete_comment(data):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such comment"
        )
    return {"success": True}


@celebrity_iq_router.get("/api/is_admin", dependencies=[Depends(require_admin)])
async def is_admin(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {"success": True}


@celebrity_iq_router.get("/")
async def index():
    return local_file("index.html")
