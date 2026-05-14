from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from app.api.v1.schemas.reservation import ReservationCreate, ReservationPatch, ReservationResponse, ReservationUpdate


class ReservationRepository(Protocol):
    def list(self, room_id: UUID | None = None, selected_date: date | None = None, user_id: UUID | None = None) -> list[ReservationResponse]:
        ...

    def get(self, reservation_id: UUID) -> ReservationResponse:
        ...

    def create(self, payload: ReservationCreate, user_id: UUID) -> ReservationResponse:
        ...

    def update(self, reservation_id: UUID, payload: ReservationUpdate, user_id: UUID) -> ReservationResponse:
        ...

    def patch(self, reservation_id: UUID, payload: ReservationPatch, user_id: UUID) -> ReservationResponse:
        ...

    def delete(self, reservation_id: UUID, user_id: UUID) -> None:
        ...

    def bulk_delete(self, ids: list[UUID], user_id: UUID) -> None:
        ...
