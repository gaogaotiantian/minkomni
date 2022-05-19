import os

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..util import local_file
from .token_holder import TokenHolder

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

token_holder = TokenHolder()

@auth_router.post("/token")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == os.getenv("ADMIN_USERNAME", "") and \
        form_data.password == os.getenv("ADMIN_PASSWORD", ""):
        token = token_holder.generate_token()
        return local_file(
            "auth_success.html",
            templated=True,
            context={"request": request, "token": token}
        )
    return "Authentication Failed"


@auth_router.get("/")
async def index(request: Request):
    return local_file("index.html")


async def require_admin(token: str = Depends(oauth2_scheme)):
    if not token_holder.check_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@auth_router.get("/test", dependencies=[Depends(require_admin)])
async def index(request: Request):
    return local_file("index.html")

