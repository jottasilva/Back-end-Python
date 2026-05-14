from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import TokenPayload, get_current_user
from app.api.v1.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.api.v1.schemas.room import RoomResponse
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_room_repository import SqlAlchemyRoomRepository

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationResponse])
def list_locations(
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LocationResponse]:
    return SqlAlchemyRoomRepository(db).list_locations()


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LocationResponse:
    return SqlAlchemyRoomRepository(db).create_location(payload)


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: UUID,
    payload: LocationUpdate,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LocationResponse:
    return SqlAlchemyRoomRepository(db).update_location(location_id, payload)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: UUID,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    SqlAlchemyRoomRepository(db).delete_location(location_id)


@router.get("/{location_id}/rooms", response_model=list[RoomResponse])
def list_rooms_by_location(
    location_id: UUID,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RoomResponse]:
    return SqlAlchemyRoomRepository(db).list_rooms(location_id=location_id)
