from uuid import UUID

from app.api.v1.schemas.reservation import ReservationCreate, ReservationResponse
from app.application.interfaces.reservation_repository import ReservationRepository


def create_reservation(repository: ReservationRepository, payload: ReservationCreate, user_id: UUID) -> ReservationResponse:
    return repository.create(payload, user_id)
