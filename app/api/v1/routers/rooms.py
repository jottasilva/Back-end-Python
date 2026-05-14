from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import TokenPayload, get_current_user
from app.api.v1.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_room_repository import SqlAlchemyRoomRepository

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(
    location_id: UUID | None = Query(default=None),
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RoomResponse]:
    return SqlAlchemyRoomRepository(db).list_rooms(location_id=location_id)


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return SqlAlchemyRoomRepository(db).create_room(payload)


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: UUID,
    payload: RoomUpdate,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return SqlAlchemyRoomRepository(db).update_room(room_id, payload)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: UUID,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    SqlAlchemyRoomRepository(db).delete_room(room_id)
