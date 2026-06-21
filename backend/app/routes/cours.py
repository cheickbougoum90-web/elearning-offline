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
    cours = Cours(
        titre=cours_data.titre,
        description=cours_data.description,
        prof_id=current_user.id
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
