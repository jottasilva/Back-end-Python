from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models import LocationModel, RoomModel

LOCATIONS = [
    {
        "id": UUID("11111111-1111-1111-1111-111111111111"),
        "name": "Matriz Paulista",
        "address": "Av. Paulista, 1000",
    },
    {
        "id": UUID("22222222-2222-2222-2222-222222222222"),
        "name": "Filial Pinheiros",
        "address": "Rua dos Pinheiros, 540",
    },
]

ROOMS = [
    ("33333333-3333-3333-3333-333333333331", "11111111-1111-1111-1111-111111111111", "Sala Agora", 8),
    ("33333333-3333-3333-3333-333333333332", "11111111-1111-1111-1111-111111111111", "Sala Panorama", 12),
    ("33333333-3333-3333-3333-333333333333", "22222222-2222-2222-2222-222222222222", "Sala Conceito", 6),
    ("33333333-3333-3333-3333-333333333334", "22222222-2222-2222-2222-222222222222", "Sala Inovacao", 10),
    ("33333333-3333-3333-3333-333333333335", "11111111-1111-1111-1111-111111111111", "Sala Strategy", 16),
]


def seed_database(db: Session) -> None:
    if db.query(LocationModel).count() > 0:
        return

    for location in LOCATIONS:
        db.add(LocationModel(**location))

    for room_id, location_id, name, capacity in ROOMS:
        db.add(
            RoomModel(
                id=UUID(room_id),
                location_id=UUID(location_id),
                name=name,
                capacity=capacity,
                image_url="https://images.unsplash.com/photo-1517502884422-41eaead166d4?auto=format&fit=crop&w=320&q=80",
            )
        )

    db.commit()
