from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import json

from app.database import get_db
from app.models.cours import Cours
from app.schemas.cours import CoursCreate, CoursUpdate, CoursResponse
from app.auth import get_current_user, require_role
from app.cache import cache_get, cache_set, cache_delete_pattern

router = APIRouter(prefix="/api/cours", tags=["Cours"])

def _to_response(c: Cours) -> dict:
    return {
        "id": c.id,
        "titre": c.titre,
        "description": c.description,
        "prof_id": c.prof_id,
        "prof_nom": c.professeur.nom if c.professeur else None,
        "moyenne_notes": c.moyenne_notes,
        "created_at": c.created_at,
    }

@router.get("/", response_model=List[CoursResponse])
def get_cours(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cours = db.query(Cours).options(joinedload(Cours.professeur)).all()
    return [_to_response(c) for c in cours]

@router.get("/{cours_id}", response_model=CoursResponse)
def get_cours_by_id(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cours = db.query(Cours).options(joinedload(Cours.professeur)).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    return _to_response(cours)

@router.post("/", response_model=CoursResponse)
def create_cours(
    cours_data: CoursCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    # Un admin peut assigner le cours à un professeur précis.
    # Un professeur crée toujours pour lui-même (prof_id ignoré si fourni).
    if current_user.role == "admin" and cours_data.prof_id:
        from app.models.utilisateur import Utilisateur
        prof = db.query(Utilisateur).filter(
            Utilisateur.id == cours_data.prof_id,
            Utilisateur.role == "professeur"
        ).first()
        if not prof:
            raise HTTPException(status_code=400, detail="Professeur invalide")
        assigned_prof_id = prof.id
    else:
        assigned_prof_id = current_user.id

    cours = Cours(
        titre=cours_data.titre,
        description=cours_data.description,
        prof_id=assigned_prof_id
    )
    db.add(cours)
    db.commit()
    db.refresh(cours)
    cache_delete_pattern("cours:*")
    return _to_response(cours)

@router.put("/{cours_id}", response_model=CoursResponse)
def update_cours(
    cours_id: int,
    cours_data: CoursUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    cours = db.query(Cours).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if current_user.role == "professeur" and cours.prof_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres cours")

    if cours_data.titre:       cours.titre       = cours_data.titre
    if cours_data.description: cours.description = cours_data.description

    db.commit()
    db.refresh(cours)
    cache_delete_pattern("cours:*")
    return _to_response(cours)

@router.delete("/{cours_id}")
def delete_cours(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    cours = db.query(Cours).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if current_user.role == "professeur" and cours.prof_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres cours")

    db.delete(cours)
    db.commit()
    cache_delete_pattern("cours:*")
    return {"message": f"Cours {cours_id} supprimé"}

@router.get("/prof/{prof_id}/stats")
def get_prof_stats(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Statistiques du tableau de bord professeur :
    nombre de cours, nombre de quiz créés, nombre d'élèves touchés,
    note moyenne sur tous ses cours."""
    from app.models.lecon import Lecon
    from app.models.quiz import Quiz
    from app.models.progression import Progression
    from app.models.avis import Avis
    from sqlalchemy import func

    mes_cours = db.query(Cours).filter(Cours.prof_id == prof_id).all()
    mes_cours_ids = [c.id for c in mes_cours]

    nombre_cours = len(mes_cours)

    nombre_quiz = 0
    nombre_etudiants = 0
    note_moyenne = 0.0

    if mes_cours_ids:
        nombre_quiz = db.query(Quiz).join(Lecon).filter(
            Lecon.cours_id.in_(mes_cours_ids)
        ).count()

        nombre_etudiants = db.query(Progression.user_id).join(Lecon).filter(
            Lecon.cours_id.in_(mes_cours_ids)
        ).distinct().count()

        moyenne = db.query(func.avg(Avis.note)).filter(
            Avis.cours_id.in_(mes_cours_ids)
        ).scalar()
        note_moyenne = round(float(moyenne), 1) if moyenne else 0.0

    return {
        "nombre_cours": nombre_cours,
        "nombre_quiz": nombre_quiz,
        "nombre_etudiants": nombre_etudiants,
        "note_moyenne": note_moyenne
    }
