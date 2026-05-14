from datetime import date
from uuid import UUID

from app.api.v1.schemas.reservation import ReservationResponse
from app.application.interfaces.reservation_repository import ReservationRepository


def list_reservations(
    repository: ReservationRepository,
    room_id: UUID | None = None,
    selected_date: date | None = None,
    user_id: UUID | None = None,
) -> list[ReservationResponse]:
    return repository.list(room_id=room_id, selected_date=selected_date, user_id=user_id)
