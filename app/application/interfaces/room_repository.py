from typing import Protocol
from uuid import UUID

from app.api.v1.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.api.v1.schemas.room import RoomCreate, RoomResponse, RoomUpdate


class RoomRepository(Protocol):
    def list_locations(self) -> list[LocationResponse]:
        ...

    def create_location(self, payload: LocationCreate) -> LocationResponse:
        ...

    def update_location(self, location_id: UUID, payload: LocationUpdate) -> LocationResponse:
        ...

    def delete_location(self, location_id: UUID) -> None:
        ...

    def list_rooms(self, location_id: UUID | None = None) -> list[RoomResponse]:
        ...

    def create_room(self, payload: RoomCreate) -> RoomResponse:
        ...

    def update_room(self, room_id: UUID, payload: RoomUpdate) -> RoomResponse:
        ...
