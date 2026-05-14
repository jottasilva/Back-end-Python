from uuid import UUID

from app.api.v1.schemas.room import RoomResponse
from app.application.interfaces.room_repository import RoomRepository


def list_rooms(repository: RoomRepository, location_id: UUID | None = None) -> list[RoomResponse]:
    return repository.list_rooms(location_id=location_id)
