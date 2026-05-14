import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-characters"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./booking_api_startup_test.db"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Base, LocationModel, RoomModel
from app.main import app

JWT_SECRET = os.environ["JWT_SECRET"]
USER_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
ROOM_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
LOCATION_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


def make_token(user_id: UUID = USER_ID) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "email": "jefferson@teste.com",
            "name": "Usuario Teste",
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def make_payload(title: str, start_time: str, end_time: str) -> dict[str, object]:
    return {
        "roomId": str(ROOM_ID),
        "responsibleName": "Usuario Teste",
        "title": title,
        "description": "Reserva criada por teste de integracao",
        "startTime": start_time,
        "endTime": end_time,
        "coffeeService": False,
        "attendeesCount": 2,
    }


def build_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with testing_session() as db:
        seed_test_data(db)

    def override_get_db() -> Session:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def seed_test_data(db: Session) -> None:
    db.add(LocationModel(id=LOCATION_ID, name="Matriz Teste", address="Rua dos Testes, 100"))
    db.add(
        RoomModel(
            id=ROOM_ID,
            location_id=LOCATION_ID,
            name="Sala Integracao",
            capacity=8,
            image_url="https://example.com/room.jpg",
        )
    )
    db.commit()


def test_create_reservation_requires_jwt() -> None:
    with build_client() as client:
        response = client.post(
            "/api/v1/reservations",
            json=make_payload("Sem token", "2026-06-20T13:00:00Z", "2026-06-20T14:00:00Z"),
        )

    assert response.status_code == 401


def test_create_reservation_with_valid_token() -> None:
    with build_client() as client:
        response = client.post(
            "/api/v1/reservations",
            headers={"Authorization": f"Bearer {make_token()}"},
            json=make_payload("Reserva valida", "2026-06-20T13:00:00Z", "2026-06-20T14:00:00Z"),
        )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Reserva valida"
    assert body["roomId"] == str(ROOM_ID)
    assert body["locationName"] == "Matriz Teste"
    assert body["userId"] == str(USER_ID)


def test_create_reservation_rejects_time_conflict() -> None:
    with build_client() as client:
        headers = {"Authorization": f"Bearer {make_token()}"}
        first = client.post(
            "/api/v1/reservations",
            headers=headers,
            json=make_payload("Reserva original", "2026-06-20T13:00:00Z", "2026-06-20T14:00:00Z"),
        )
        conflict = client.post(
            "/api/v1/reservations",
            headers=headers,
            json=make_payload("Reserva conflitante", "2026-06-20T13:30:00Z", "2026-06-20T14:30:00Z"),
        )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert "Ja existe reserva" in conflict.json()["detail"]


def test_create_reservation_rejects_past_start_time() -> None:
    past = datetime(2020, 1, 1, 13, 0, tzinfo=timezone.utc).isoformat()
    past_end = datetime(2020, 1, 1, 14, 0, tzinfo=timezone.utc).isoformat()

    with build_client() as client:
        response = client.post(
            "/api/v1/reservations",
            headers={"Authorization": f"Bearer {make_token(uuid4())}"},
            json=make_payload("Reserva no passado", past, past_end),
        )

    assert response.status_code == 422
