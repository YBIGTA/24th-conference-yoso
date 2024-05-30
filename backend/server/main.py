import numpy as np
import json
from fastapi import FastAPI
from server.database import vector, document, graph
from pydantic import BaseModel
from .routers import search, paper

app = FastAPI(
    title="YOSO API Documentation",
    version="0.2.0"
)
app.include_router(
    router=search.router,
    prefix="/api/v1"
)
app.include_router(
    router=paper.router,
    prefix="/api/v1"
)


@app.get("/ping", summary="접속 테스트")
def read_root():
    return "pong"
