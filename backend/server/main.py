from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, paper

app = FastAPI(
    title="YOSO API Documentation",
    version="0.4.0"
)

# Routers
app.include_router(
    router=search.router,
    prefix="/api/v1"
)
app.include_router(
    router=paper.router,
    prefix="/api/v1"
)

# Middlewares
origins = [
    # Future: Only allows deployed frontend web server
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", summary="접속 테스트")
def read_root():
    return "pong"
