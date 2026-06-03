from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.progression import Progression
from app.models.lecon import Lecon
from app.models.cours import Cours
from app.schemas.progression import ProgressionCreate, ProgressionResponse, ProgressionStats
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/progression", tags=["Progression"])

@router.get("/{user_id}", response_model=List[ProgressionResponse])
def get_progression(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Un élève ne peut voir que sa propre progression
    if current_user.role == "eleve" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return db.query(Progression).filter(
        Progression.user_id == user_id
    ).all()

@router.post("/", response_model=ProgressionResponse)
def save_progression(
    prog_data: ProgressionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("eleve"))
):
    # Vérifier si une progression existe déjà
    existing = db.query(Progression).filter(
        Progression.user_id == current_user.id,
        Progression.lecon_id == prog_data.lecon_id
    ).first()

    if existing:
        # Mettre à jour
        existing.statut = prog_data.statut
        existing.score  = prog_data.score
        existing.synced = False  # à resynchroniser
        db.commit()
        db.refresh(existing)
        return existing

    # Créer nouvelle progression
    progression = Progression(
        user_id=current_user.id,
        lecon_id=prog_data.lecon_id,
        statut=prog_data.statut,
        score=prog_data.score,
        synced=False  # offline par défaut
    )
    db.add(progression)
    db.commit()
    db.refresh(progression)
    return progression

@router.get("/{user_id}/stats", response_model=ProgressionStats)
def get_stats(
    user_id: int,
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Total leçons du cours
    total = db.query(Lecon).filter(Lecon.cours_id == cours_id).count()

    # Leçons terminées par l'élève
    terminees = db.query(Progression).join(Lecon).filter(
        Progression.user_id == user_id,
        Progression.statut == "termine",
        Lecon.cours_id == cours_id
    ).count()

    # Score moyen
    progressions = db.query(Progression).join(Lecon).filter(
        Progression.user_id == user_id,
        Lecon.cours_id == cours_id
    ).all()

    score_moyen = sum(p.score for p in progressions) / len(progressions) if progressions else 0.0
    pourcentage = (terminees / total * 100) if total > 0 else 0.0

    return ProgressionStats(
        total_lecons=total,
        lecons_terminees=terminees,
        pourcentage=round(pourcentage, 1),
        score_moyen=round(score_moyen, 1)
    )
