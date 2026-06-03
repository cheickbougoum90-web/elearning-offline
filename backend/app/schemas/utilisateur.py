from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UtilisateurBase(BaseModel):
    nom: str
    email: EmailStr
    role: str  # eleve | professeur | admin

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurResponse(UtilisateurBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    nom: str
