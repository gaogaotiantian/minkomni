from fastapi import FastAPI
from .singless.api import singlessAPI

app = FastAPI()

app.include_router(singlessAPI, prefix="/singless")

@app.get("/")
async def root():
    return {"message": "Hello"}