from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .singless.api import singlessAPI

import os

file_dir = os.path.dirname(__file__)
templates = Jinja2Templates(
    directory=os.path.join(file_dir, "templates")
)

app = FastAPI()

app.include_router(singlessAPI, prefix="/singless")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
