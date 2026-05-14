from uuid import UUID

from sqlalchemy.orm import Session

from app.api.v1.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.api.v1.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.domain.exceptions import LocationConflictError, ReservationNotFoundError, RoomConflictError
from app.infrastructure.database.models import LocationModel, ReservationModel, RoomModel


class SqlAlchemyRoomRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_locations(self) -> list[LocationResponse]:
        locations = self._db.query(LocationModel).order_by(LocationModel.name).all()
        return [LocationResponse.model_validate(location) for location in locations]

    def create_location(self, payload: LocationCreate) -> LocationResponse:
        location = LocationModel(name=payload.name.strip(), address=payload.address.strip())
        self._db.add(location)
        self._db.commit()
        self._db.refresh(location)
        return LocationResponse.model_validate(location)

    def update_location(self, location_id: UUID, payload: LocationUpdate) -> LocationResponse:
        location = self._get_location(location_id)
        location.name = payload.name.strip()
        location.address = payload.address.strip()
        self._db.commit()
        self._db.refresh(location)
        return LocationResponse.model_validate(location)

    def delete_location(self, location_id: UUID) -> None:
        location = self._get_location(location_id)
        has_rooms = self._db.query(RoomModel.id).filter(RoomModel.location_id == location_id).first()
        if has_rooms:
            raise LocationConflictError("Nao e possivel excluir uma unidade com salas vinculadas.")

        self._db.delete(location)
        self._db.commit()

    def list_rooms(self, location_id: UUID | None = None) -> list[RoomResponse]:
        query = self._db.query(RoomModel).join(RoomModel.location).order_by(RoomModel.name)
        if location_id:
            query = query.filter(RoomModel.location_id == location_id)

        return [self._to_response(room) for room in query.all()]

    def create_room(self, payload: RoomCreate) -> RoomResponse:
        self._ensure_location_exists(payload.location_id)
        room = RoomModel(
            location_id=payload.location_id,
            name=payload.name,
            capacity=payload.capacity,
            image_url=payload.image_url,
        )
        self._db.add(room)
        self._db.commit()
        self._db.refresh(room)
        return self._to_response(room)

    def update_room(self, room_id: UUID, payload: RoomUpdate) -> RoomResponse:
        room = self._get_room(room_id)
        self._ensure_location_exists(payload.location_id)
        room.location_id = payload.location_id
        room.name = payload.name
        room.capacity = payload.capacity
        room.image_url = payload.image_url
        self._db.commit()
        self._db.refresh(room)
        return self._to_response(room)

    def delete_room(self, room_id: UUID) -> None:
        room = self._get_room(room_id)
        has_reservations = self._db.query(ReservationModel.id).filter(ReservationModel.room_id == room_id).first()
        if has_reservations:
            raise RoomConflictError("Nao e possivel excluir uma sala com reservas vinculadas.")

        self._db.delete(room)
        self._db.commit()

    def _ensure_location_exists(self, location_id: UUID) -> None:
        self._get_location(location_id)

    def _get_location(self, location_id: UUID) -> LocationModel:
        location = self._db.query(LocationModel).filter(LocationModel.id == location_id).first()
        if not location:
            raise ReservationNotFoundError("Local nao encontrado.")
        return location

    def _get_room(self, room_id: UUID) -> RoomModel:
        room = self._db.query(RoomModel).filter(RoomModel.id == room_id).first()
        if not room:
            raise ReservationNotFoundError("Sala nao encontrada.")
        return room

    def _to_response(self, room: RoomModel) -> RoomResponse:
        return RoomResponse(
            id=room.id,
            location_id=room.location_id,
            location_name=room.location.name,
            name=room.name,
            capacity=room.capacity,
            image_url=room.image_url,
            available=True,
            available_until=None,
        )
