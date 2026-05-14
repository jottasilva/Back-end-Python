from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Location:
    id: UUID
    name: str
    address: str
    created_at: datetime
