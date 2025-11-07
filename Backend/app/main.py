from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, collections
from .config import settings
from .db import Base, engine

app = FastAPI(title="Cotiza-inador API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/ping")
def ping() -> dict[str, bool]:
    return {"pong": True}


app.include_router(auth.router)
app.include_router(collections.router)

