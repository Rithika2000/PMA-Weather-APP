from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import QueryRecord
from ..schemas import RecordCreate, RecordOut, RecordUpdate, RangeRequest
from ..crud import create_record, get_record, list_records, delete_record
from .weather import range_weather  # reuse for re-fetch logic

router = APIRouter(prefix="/records", tags=["records"])

@router.get("/", response_model=list[RecordOut])
def api_list_records(db: Session = Depends(get_db)):
    return list_records(db)

@router.get("/{record_id}", response_model=RecordOut)
def api_get_record(record_id: int, db: Session = Depends(get_db)):
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(404, "Record not found")
    return rec

@router.post("/", response_model=RecordOut)
def api_create_record(body: RecordCreate, db: Session = Depends(get_db)):
    # Validate location & range by calling weather.range (will raise on error)
    rr = RangeRequest(input_location=body.input_location, start_date=body.start_date, end_date=body.end_date)
    payload = range_weather(rr)["payload"]
    resolved = payload.get("resolved", {})
    rec = QueryRecord(
        input_location=body.input_location.strip(),
        resolved_name=resolved.get("name"),
        lat=resolved.get("lat"),
        lon=resolved.get("lon"),
        kind="range",
        start_date=body.start_date,
        end_date=body.end_date,
        result_payload=payload
    )
    return create_record(db, rec)

@router.patch("/{record_id}", response_model=RecordOut)
def api_update_record(record_id: int, body: RecordUpdate, db: Session = Depends(get_db)):
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(404, "Record not found")

    # apply updates
    if body.input_location is not None:
        rec.input_location = body.input_location.strip()
    if body.resolved_name is not None:
        rec.resolved_name = body.resolved_name
    if body.kind is not None:
        rec.kind = body.kind
    if body.start_date is not None:
        rec.start_date = body.start_date
    if body.end_date is not None:
        rec.end_date = body.end_date
        if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
            raise HTTPException(400, "end_date must be on/after start_date")

    # re-fetch using the range endpoint if kind==range
    if body.refetch and rec.kind == "range" and rec.start_date and rec.end_date:
        rr = RangeRequest(input_location=rec.input_location, start_date=rec.start_date, end_date=rec.end_date)
        payload = range_weather(rr)["payload"]
        resolved = payload.get("resolved", {})
        rec.resolved_name = resolved.get("name")
        rec.lat = resolved.get("lat")
        rec.lon = resolved.get("lon")
        rec.result_payload = payload

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/{record_id}")
def api_delete_record(record_id: int, db: Session = Depends(get_db)):
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(404, "Record not found")
    delete_record(db, rec)
    return {"ok": True}
