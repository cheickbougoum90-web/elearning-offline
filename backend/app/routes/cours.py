from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.models.cours import Cours
from app.schemas.cours import CoursCreate, CoursUpdate, CoursResponse
from app.auth import get_current_user, require_role
from app.cache import cache_get, cache_set, cache_delete_pattern

router = APIRouter(prefix="/api/cours", tags=["Cours"])

@router.get("/", response_model=List[CoursResponse])
def get_cours(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Vérifier le cache d'abord
    cached = cache_get("cours:all")
    if cached:
        return json.loads(cached)

    cours = db.query(Cours).all()

    # Mettre en cache 10 minutes
    cache_set("cours:all", json.dumps([{
        "id": c.id, "titre": c.titre, "description": c.description,
        "prof_id": c.prof_id, "moyenne_notes": c.moyenne_notes,
        "created_at": str(c.created_at)
    } for c in cours]))

    return cours

@router.get("/{cours_id}", response_model=CoursResponse)
def get_cours_by_id(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    cours = db.query(Cours).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    return cours

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

    # Invalider le cache
    cache_delete_pattern("cours:*")
    return cours

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

    # Vérifier que le prof est propriétaire (sauf admin)
    if current_user.role == "professeur" and cours.prof_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres cours")

    if cours_data.titre:       cours.titre       = cours_data.titre
    if cours_data.description: cours.description = cours_data.description

    db.commit()
    db.refresh(cours)
    cache_delete_pattern("cours:*")
    return cours

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
