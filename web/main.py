import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth.auth import auth_router
from .celebrity_iq.api import celebrity_iq_router
from .discordbot import DiscordClient
from .jx3.api import jx3_router
from .singless.api import singlessAPI
from .zsxq.api import zsxq_router
from .util import local_file_path


file_dir = os.path.dirname(__file__)
templates = Jinja2Templates(
    directory=os.path.join(file_dir, "templates")
)


app = FastAPI()
app.mount("/static", StaticFiles(directory=local_file_path("static")), name="static")

app.include_router(singlessAPI, prefix="/singless")
app.include_router(auth_router, prefix="/auth")
app.include_router(celebrity_iq_router, prefix="/celebrity_iq")
app.include_router(zsxq_router, prefix="/zsxq")
app.include_router(jx3_router, prefix="/jx3")


@app.on_event("startup")
async def startup_event():
    discord_client = DiscordClient()
    asyncio.create_task(discord_client.start())


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
