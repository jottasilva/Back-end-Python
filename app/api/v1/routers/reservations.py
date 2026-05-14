from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import TokenPayload, get_current_user
from app.api.v1.schemas.reservation import (
    BulkDeleteRequest,
    ReservationCreate,
    ReservationPatch,
    ReservationResponse,
    ReservationUpdate,
)
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_reservation_repository import SqlAlchemyReservationRepository

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
def list_reservations(
    room_id: UUID | None = Query(default=None),
    selected_date: date | None = Query(default=None, alias="date"),
    user_id: UUID | None = Query(default=None),
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    return SqlAlchemyReservationRepository(db).list(room_id=room_id, selected_date=selected_date, user_id=user_id)


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    return SqlAlchemyReservationRepository(db).create(payload, current_user.user_id)


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: UUID,
    _: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    return SqlAlchemyReservationRepository(db).get(reservation_id)


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: UUID,
    payload: ReservationUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    return SqlAlchemyReservationRepository(db).update(reservation_id, payload, current_user.user_id)


@router.patch("/{reservation_id}", response_model=ReservationResponse)
def patch_reservation(
    reservation_id: UUID,
    payload: ReservationPatch,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    return SqlAlchemyReservationRepository(db).patch(reservation_id, payload, current_user.user_id)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    SqlAlchemyReservationRepository(db).delete(reservation_id, current_user.user_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_reservations(
    payload: BulkDeleteRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    SqlAlchemyReservationRepository(db).bulk_delete(payload.ids, current_user.user_id)
