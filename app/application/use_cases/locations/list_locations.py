from app.api.v1.schemas.location import LocationResponse
from app.application.interfaces.room_repository import RoomRepository


def list_locations(repository: RoomRepository) -> list[LocationResponse]:
    return repository.list_locations()
