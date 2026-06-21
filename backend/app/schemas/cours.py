from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CoursBase(BaseModel):
    titre: str
    description: Optional[str] = None

class CoursCreate(CoursBase):
    prof_id: Optional[int] = None  # rempli uniquement si l'admin crée le cours

class CoursUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None

class CoursResponse(CoursBase):
    id: int
    prof_id: int
    prof_nom: Optional[str] = None
    moyenne_notes: float
    created_at: datetime

    class Config:
        from_attributes = True
