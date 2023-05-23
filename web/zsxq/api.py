from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


file_dir = os.path.dirname(__file__)
templates = Jinja2Templates(
    directory=os.path.join(file_dir, "templates")
)
zsxq_router = APIRouter()


@zsxq_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
