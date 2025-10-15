from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import QueryRecord

def create_record(db: Session, rec: QueryRecord) -> QueryRecord:
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_record(db: Session, record_id: int) -> QueryRecord | None:
    return db.get(QueryRecord, record_id)

def list_records(db: Session) -> list[QueryRecord]:
    return db.execute(select(QueryRecord).order_by(QueryRecord.created_at.desc())).scalars().all()

def delete_record(db: Session, rec: QueryRecord) -> None:
    db.delete(rec)
    db.commit()
