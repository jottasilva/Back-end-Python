import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.exception_handler import configure_exception_handlers
from app.api.v1.routers import locations, reservations, rooms
from app.infrastructure.database.connection import SessionLocal, engine
from app.infrastructure.database.models import Base
from app.infrastructure.database.seed import seed_database

app = FastAPI(title="Booking API", version="0.1.0")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_exception_handlers(app)

app.include_router(reservations.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
