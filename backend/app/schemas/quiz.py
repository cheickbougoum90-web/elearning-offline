from pydantic import BaseModel
from typing import Optional, List

class ReponseCreate(BaseModel):
    texte: str
    est_correcte: bool = False

class ReponseResponse(ReponseCreate):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    question: str

class QuizCreate(QuizBase):
    lecon_id: int
    reponses: List[ReponseCreate] = []

class QuizResponse(QuizBase):
    id: int
    lecon_id: int
    reponses: List[ReponseResponse] = []

    class Config:
        from_attributes = True

class SoumettreReponse(BaseModel):
    reponse_ids: List[int]

class ResultatQuiz(BaseModel):
    correct: bool
    score: float
    message: str
