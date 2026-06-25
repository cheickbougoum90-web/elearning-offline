from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id          = Column(Integer, primary_key=True, index=True)
    source_ip   = Column(String(50), nullable=False)
    nb_progressions = Column(Integer, default=0)
    nb_avis     = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
