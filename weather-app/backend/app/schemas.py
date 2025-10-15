from pydantic import BaseModel, field_validator, FieldValidationInfo
from datetime import date, datetime

# --- Weather payload wrappers ---
class RangeRequest(BaseModel):
    input_location: str
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v, info: FieldValidationInfo):
        # pydantic v2 passes a FieldValidationInfo; check other fields via info.data
        start = None
        try:
            start = info.data.get("start_date")
        except Exception:
            start = None
        if start is not None and v < start:
            raise ValueError("end_date must be on/after start_date")
        return v

class GeoOut(BaseModel):
    name: str
    lat: float
    lon: float

class WeatherPayload(BaseModel):
    payload: dict

# --- Records ---
class RecordCreate(BaseModel):
    input_location: str
    kind: str = "range"
    start_date: date
    end_date: date
    resolved_name: str | None = None
    lat: float | None = None
    lon: float | None = None
    result_payload: dict | None = None

class RecordOut(BaseModel):
    id: int
    input_location: str
    resolved_name: str | None
    lat: float
    lon: float
    kind: str
    start_date: date | None
    end_date: date | None
    created_at: datetime

    class Config:
        from_attributes = True

class RecordUpdate(BaseModel):
    input_location: str | None = None
    resolved_name: str | None = None
    kind: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    refetch: bool = True  # if true, refresh result_payload based on updates
