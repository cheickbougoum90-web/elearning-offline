from pydantic import BaseModel
from typing import Optional

class LeconBase(BaseModel):
    titre: str
    contenu: Optional[str] = None
    ordre: int = 1

class LeconCreate(LeconBase):
    cours_id: int

class LeconUpdate(BaseModel):
    titre: Optional[str] = None
    contenu: Optional[str] = None
    ordre: Optional[int] = None

class LeconResponse(LeconBase):
    id: int
    cours_id: int

    class Config:
        from_attributes = True

class MediaCreate(BaseModel):
    type: str   # image | video
    url: str
    ordre: int = 1

class MediaResponse(MediaCreate):
    id: int
    lecon_id: int

    class Config:
        from_attributes = True
