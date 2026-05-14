from __future__ import annotations

from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.v1.schemas.reservation import (
    ReservationCreate,
    ReservationPatch,
    ReservationResponse,
    ReservationUpdate,
)
from app.domain.exceptions import ReservationConflictError, ReservationForbiddenError, ReservationNotFoundError
from app.infrastructure.database.models import ReservationModel, RoomModel


class SqlAlchemyReservationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        room_id: UUID | None = None,
        selected_date: date | None = None,
        user_id: UUID | None = None,
    ) -> list[ReservationResponse]:
        query = self._db.query(ReservationModel).join(ReservationModel.room).join(RoomModel.location)

        if room_id:
            query = query.filter(ReservationModel.room_id == room_id)
        if user_id:
            query = query.filter(ReservationModel.user_id == user_id)
        if selected_date:
            start = datetime.combine(selected_date, time.min, tzinfo=timezone.utc)
            end = datetime.combine(selected_date, time.max, tzinfo=timezone.utc)
            query = query.filter(ReservationModel.start_time >= start, ReservationModel.start_time <= end)

        reservations = query.order_by(ReservationModel.start_time.asc()).all()
        return [self._to_response(reservation) for reservation in reservations]

    def get(self, reservation_id: UUID) -> ReservationResponse:
        return self._to_response(self._get_model(reservation_id))

    def create(self, payload: ReservationCreate, user_id: UUID) -> ReservationResponse:
        self._ensure_room_exists(payload.room_id)
        self._ensure_no_conflict(payload.room_id, payload.start_time, payload.end_time)

        reservation = ReservationModel(
            room_id=payload.room_id,
            user_id=user_id,
            responsible_name=payload.responsible_name,
            title=payload.title,
            description=payload.description,
            start_time=payload.start_time,
            end_time=payload.end_time,
            coffee_service=payload.coffee_service,
            attendees_count=payload.attendees_count,
        )

        self._db.add(reservation)
        self._db.commit()
        self._db.refresh(reservation)
        return self._to_response(reservation)

    def update(self, reservation_id: UUID, payload: ReservationUpdate, user_id: UUID) -> ReservationResponse:
        reservation = self._get_owned_model(reservation_id, user_id)
        self._ensure_room_exists(payload.room_id)
        self._ensure_no_conflict(payload.room_id, payload.start_time, payload.end_time, exclude_id=reservation.id)

        reservation.room_id = payload.room_id
        reservation.responsible_name = payload.responsible_name
        reservation.title = payload.title
        reservation.description = payload.description
        reservation.start_time = payload.start_time
        reservation.end_time = payload.end_time
        reservation.coffee_service = payload.coffee_service
        reservation.attendees_count = payload.attendees_count

        self._db.commit()
        self._db.refresh(reservation)
        return self._to_response(reservation)

    def patch(self, reservation_id: UUID, payload: ReservationPatch, user_id: UUID) -> ReservationResponse:
        reservation = self._get_owned_model(reservation_id, user_id)
        data = payload.model_dump(exclude_unset=True)

        room_id = data.get("room_id", reservation.room_id)
        start_time = data.get("start_time", reservation.start_time)
        end_time = data.get("end_time", reservation.end_time)

        if end_time <= start_time:
            raise ReservationConflictError("O horario de fim deve ser maior que o horario de inicio.")

        self._ensure_room_exists(room_id)
        self._ensure_no_conflict(room_id, start_time, end_time, exclude_id=reservation.id)

        for key, value in data.items():
            setattr(reservation, key, value)

        self._db.commit()
        self._db.refresh(reservation)
        return self._to_response(reservation)

    def delete(self, reservation_id: UUID, user_id: UUID) -> None:
        reservation = self._get_owned_model(reservation_id, user_id)
        self._db.delete(reservation)
        self._db.commit()

    def bulk_delete(self, ids: list[UUID], user_id: UUID) -> None:
        reservations = self._db.query(ReservationModel).filter(ReservationModel.id.in_(ids)).all()
        if len(reservations) != len(set(ids)):
            raise ReservationNotFoundError("Uma ou mais reservas nao foram encontradas.")

        for reservation in reservations:
            if reservation.user_id != user_id:
                raise ReservationForbiddenError("Somente o dono da reserva pode excluir.")
            self._db.delete(reservation)

        self._db.commit()

    def _ensure_no_conflict(
        self,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: UUID | None = None,
    ) -> None:
        query = self._db.query(ReservationModel).filter(
            and_(
                ReservationModel.room_id == room_id,
                start_time < ReservationModel.end_time,
                end_time > ReservationModel.start_time,
            )
        )
        if exclude_id:
            query = query.filter(ReservationModel.id != exclude_id)

        if query.with_for_update().first() is not None:
            raise ReservationConflictError("Ja existe reserva para esta sala neste horario.")

    def _ensure_room_exists(self, room_id: UUID) -> None:
        exists = self._db.query(RoomModel.id).filter(RoomModel.id == room_id).first()
        if not exists:
            raise ReservationNotFoundError("Sala nao encontrada.")

    def _get_model(self, reservation_id: UUID) -> ReservationModel:
        reservation = self._db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
        if not reservation:
            raise ReservationNotFoundError("Reserva nao encontrada.")
        return reservation

    def _get_owned_model(self, reservation_id: UUID, user_id: UUID) -> ReservationModel:
        reservation = self._get_model(reservation_id)
        if reservation.user_id != user_id:
            raise ReservationForbiddenError("Somente o dono da reserva pode alterar ou excluir.")
        return reservation

    def _to_response(self, reservation: ReservationModel) -> ReservationResponse:
        return ReservationResponse(
            id=reservation.id,
            room_id=reservation.room_id,
            room_name=reservation.room.name,
            location_id=reservation.room.location_id,
            location_name=reservation.room.location.name,
            user_id=reservation.user_id,
            responsible_name=reservation.responsible_name,
            title=reservation.title,
            description=reservation.description,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            coffee_service=reservation.coffee_service,
            attendees_count=reservation.attendees_count,
            status="confirmed",
        )
