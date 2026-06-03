from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProgressionCreate(BaseModel):
    lecon_id: int
    statut: str = "en_cours"   # en_cours | termine
    score: float = 0.0

class ProgressionResponse(BaseModel):
    id: int
    user_id: int
    lecon_id: int
    statut: str
    score: float
    synced: bool
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressionStats(BaseModel):
    total_lecons: int
    lecons_terminees: int
    pourcentage: float
    score_moyen: float
