from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Date, DateTime, Integer, JSON
from datetime import datetime
from .db import Base

class QueryRecord(Base):
    __tablename__ = "queries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    input_location: Mapped[str] = mapped_column(String, nullable=False)
    resolved_name: Mapped[str | None] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)  # 'current'|'forecast'|'range'
    start_date: Mapped[Date | None] = mapped_column(Date)
    end_date: Mapped[Date | None] = mapped_column(Date)
    result_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
