from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Room:
    id: UUID
    location_id: UUID
    name: str
    capacity: int
    created_at: datetime
