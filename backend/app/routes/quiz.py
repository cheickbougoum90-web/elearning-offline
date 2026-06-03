from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.quiz import Quiz
from app.models.reponse import Reponse
from app.schemas.quiz import QuizCreate, QuizResponse, SoumettreReponse, ResultatQuiz
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])

@router.get("/lecon/{lecon_id}", response_model=List[QuizResponse])
def get_quiz_by_lecon(
    lecon_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Quiz).filter(Quiz.lecon_id == lecon_id).all()

@router.post("/", response_model=QuizResponse)
def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    # Créer le quiz
    quiz = Quiz(question=quiz_data.question, lecon_id=quiz_data.lecon_id)
    db.add(quiz)
    db.flush()  # obtenir l'id sans commiter

    # Créer les réponses associées
    for rep_data in quiz_data.reponses:
        reponse = Reponse(
            quiz_id=quiz.id,
            texte=rep_data.texte,
            est_correcte=rep_data.est_correcte
        )
        db.add(reponse)

    db.commit()
    db.refresh(quiz)
    return quiz

@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")
    db.delete(quiz)
    db.commit()
    return {"message": f"Quiz {quiz_id} supprimé"}

@router.post("/{quiz_id}/soumettre", response_model=ResultatQuiz)
def soumettre_reponse(
    quiz_id: int,
    soumission: SoumettreReponse,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("eleve"))
):
    # Vérifier que le quiz existe
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")

    # Vérifier la réponse choisie
    reponse = db.query(Reponse).filter(
        Reponse.id == soumission.reponse_id,
        Reponse.quiz_id == quiz_id
    ).first()
    if not reponse:
        raise HTTPException(status_code=404, detail="Réponse introuvable")

    correct = reponse.est_correcte
    score   = 100.0 if correct else 0.0

    return ResultatQuiz(
        correct=correct,
        score=score,
        message="Bonne réponse ! 🎉" if correct else "Mauvaise réponse. Réessaie !"
    )
