from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class AvisCreate(BaseModel):
    cours_id: int
    note: int
    commentaire: Optional[str] = None

    @validator("note")
    def note_valide(cls, v):
        if v < 1 or v > 5:
            raise ValueError("La note doit être entre 1 et 5")
        return v

class AvisResponse(BaseModel):
    id: int
    user_id: int
    cours_id: int
    note: int
    commentaire: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ClassementProfesseur(BaseModel):
    prof_id: int
    nom: str
    nombre_cours: int
    nombre_avis: int
    moyenne: float
