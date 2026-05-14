from uuid import UUID

from app.application.interfaces.reservation_repository import ReservationRepository


def bulk_delete_reservations(repository: ReservationRepository, ids: list[UUID], user_id: UUID) -> None:
    repository.bulk_delete(ids, user_id)
