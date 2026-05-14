from uuid import UUID

from app.api.v1.schemas.reservation import ReservationResponse, ReservationUpdate
from app.application.interfaces.reservation_repository import ReservationRepository


def update_reservation(
    repository: ReservationRepository,
    reservation_id: UUID,
    payload: ReservationUpdate,
    user_id: UUID,
) -> ReservationResponse:
    return repository.update(reservation_id, payload, user_id)
