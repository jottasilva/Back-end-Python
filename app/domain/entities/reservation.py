from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Reservation:
    id: UUID
    room_id: UUID
    user_id: UUID
    responsible_name: str
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    coffee_service: bool
    attendees_count: int
    created_at: datetime
    updated_at: datetime
