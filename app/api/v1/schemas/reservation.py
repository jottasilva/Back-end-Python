from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def ensure_future_start(value: datetime) -> None:
    if value <= datetime.now(timezone.utc):
        raise ValueError("startTime must be in the future")


class ReservationBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    room_id: UUID = Field(validation_alias="roomId", serialization_alias="roomId")
    responsible_name: str = Field(min_length=1, max_length=120, validation_alias="responsibleName", serialization_alias="responsibleName")
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    start_time: datetime = Field(validation_alias="startTime", serialization_alias="startTime")
    end_time: datetime = Field(validation_alias="endTime", serialization_alias="endTime")
    coffee_service: bool = Field(default=False, validation_alias="coffeeService", serialization_alias="coffeeService")
    attendees_count: int = Field(default=1, ge=1, validation_alias="attendeesCount", serialization_alias="attendeesCount")

    @field_validator("start_time", "end_time")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("datetime must include timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationBase":
        if self.end_time <= self.start_time:
            raise ValueError("endTime must be greater than startTime")
        return self


class ReservationCreate(ReservationBase):
    @model_validator(mode="after")
    def validate_future_start(self) -> "ReservationCreate":
        ensure_future_start(self.start_time)
        return self


class ReservationUpdate(ReservationBase):
    @model_validator(mode="after")
    def validate_future_start(self) -> "ReservationUpdate":
        ensure_future_start(self.start_time)
        return self


class ReservationPatch(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    room_id: UUID | None = Field(default=None, validation_alias="roomId", serialization_alias="roomId")
    responsible_name: str | None = Field(default=None, validation_alias="responsibleName", serialization_alias="responsibleName")
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = Field(default=None, validation_alias="startTime", serialization_alias="startTime")
    end_time: datetime | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime")
    coffee_service: bool | None = Field(default=None, validation_alias="coffeeService", serialization_alias="coffeeService")
    attendees_count: int | None = Field(default=None, ge=1, validation_alias="attendeesCount", serialization_alias="attendeesCount")

    @field_validator("start_time", "end_time")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if value.tzinfo is None:
            raise ValueError("datetime must include timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_future_start(self) -> "ReservationPatch":
        if self.start_time is not None:
            ensure_future_start(self.start_time)
        return self


class BulkDeleteRequest(BaseModel):
    ids: list[UUID]


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    room_id: UUID = Field(serialization_alias="roomId")
    room_name: str = Field(serialization_alias="roomName")
    location_id: UUID = Field(serialization_alias="locationId")
    location_name: str = Field(serialization_alias="locationName")
    user_id: UUID = Field(serialization_alias="userId")
    responsible_name: str = Field(serialization_alias="responsibleName")
    title: str
    description: str | None = None
    start_time: datetime = Field(serialization_alias="startTime")
    end_time: datetime = Field(serialization_alias="endTime")
    coffee_service: bool = Field(serialization_alias="coffeeService")
    attendees_count: int = Field(serialization_alias="attendeesCount")
    status: str = "confirmed"
