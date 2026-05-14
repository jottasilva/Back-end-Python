from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoomBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    location_id: UUID = Field(validation_alias="locationId", serialization_alias="locationId")
    name: str = Field(min_length=1, max_length=120)
    capacity: int = Field(ge=1)
    image_url: str = Field(default="", validation_alias="imageUrl", serialization_alias="imageUrl")


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    location_id: UUID = Field(serialization_alias="locationId")
    location_name: str = Field(serialization_alias="locationName")
    name: str
    capacity: int
    image_url: str = Field(serialization_alias="imageUrl")
    available: bool = True
    available_until: str | None = Field(default=None, serialization_alias="availableUntil")
