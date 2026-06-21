from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.quiz import Quiz
from app.models.reponse import Reponse
from app.models.lecon import Lecon
from app.models.cours import Cours
from app.schemas.quiz import QuizCreate, QuizResponse, SoumettreReponse, ResultatQuiz
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])

def _verifier_proprietaire_quiz_lecon(lecon_id: int, current_user, db: Session) -> Lecon:
    """Vérifie que l'utilisateur est admin ou propriétaire du cours
    auquel appartient la leçon visée. Retourne la leçon si valide."""
    lecon = db.query(Lecon).filter(Lecon.id == lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon introuvable")

    if current_user.role == "admin":
        return lecon

    cours = db.query(Cours).filter(Cours.id == lecon.cours_id).first()
    if not cours or cours.prof_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que les quiz de vos propres cours"
        )
    return lecon

def _verifier_proprietaire_quiz(quiz: Quiz, current_user, db: Session):
    """Vérifie la propriété pour un quiz déjà chargé."""
    if current_user.role == "admin":
        return
    lecon = db.query(Lecon).filter(Lecon.id == quiz.lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon associée introuvable")
    cours = db.query(Cours).filter(Cours.id == lecon.cours_id).first()
    if not cours or cours.prof_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que les quiz de vos propres cours"
        )

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
    _verifier_proprietaire_quiz_lecon(quiz_data.lecon_id, current_user, db)

    if len(quiz_data.reponses) < 2:
        raise HTTPException(status_code=400, detail="Un quiz doit avoir au moins 2 réponses")

    if not any(r.est_correcte for r in quiz_data.reponses):
        raise HTTPException(status_code=400, detail="Au moins une réponse doit être correcte")

    quiz = Quiz(question=quiz_data.question, lecon_id=quiz_data.lecon_id)
    db.add(quiz)
    db.flush()

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

    _verifier_proprietaire_quiz(quiz, current_user, db)

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
    """Valide une soumission à choix multiple : la réponse est correcte
    SEULEMENT si l'élève a coché exactement toutes les bonnes réponses,
    ni plus, ni moins."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")

    toutes_reponses = db.query(Reponse).filter(Reponse.quiz_id == quiz_id).all()
    if not toutes_reponses:
        raise HTTPException(status_code=404, detail="Aucune réponse définie pour ce quiz")

    ids_corrects = set(r.id for r in toutes_reponses if r.est_correcte)
    ids_soumis   = set(soumission.reponse_ids)

    ids_valides = set(r.id for r in toutes_reponses)
    if not ids_soumis.issubset(ids_valides):
        raise HTTPException(status_code=400, detail="Une ou plusieurs réponses ne correspondent pas à ce quiz")

    correct = (ids_soumis == ids_corrects)
    score = 100.0 if correct else 0.0

    return ResultatQuiz(
        correct=correct,
        score=score,
        message="Bonne réponse ! 🎉" if correct else "Mauvaise réponse. Réessaie !"
    )
