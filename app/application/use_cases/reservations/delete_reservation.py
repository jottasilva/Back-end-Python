from uuid import UUID

from app.application.interfaces.reservation_repository import ReservationRepository


def delete_reservation(repository: ReservationRepository, reservation_id: UUID, user_id: UUID) -> None:
    repository.delete(reservation_id, user_id)
