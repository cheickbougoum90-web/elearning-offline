from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.lecon import Lecon
from app.models.media import Media
from app.schemas.lecon import LeconCreate, LeconUpdate, LeconResponse, MediaCreate, MediaResponse
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/lecons", tags=["Leçons"])

@router.get("/cours/{cours_id}", response_model=List[LeconResponse])
def get_lecons_by_cours(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Lecon).filter(
        Lecon.cours_id == cours_id
    ).order_by(Lecon.ordre).all()

@router.get("/{lecon_id}", response_model=LeconResponse)
def get_lecon(
    lecon_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    lecon = db.query(Lecon).filter(Lecon.id == lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon introuvable")
    return lecon

@router.post("/", response_model=LeconResponse)
def create_lecon(
    lecon_data: LeconCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    lecon = Lecon(
        titre=lecon_data.titre,
        contenu=lecon_data.contenu,
        cours_id=lecon_data.cours_id,
        ordre=lecon_data.ordre
    )
    db.add(lecon)
    db.commit()
    db.refresh(lecon)
    return lecon

@router.put("/{lecon_id}", response_model=LeconResponse)
def update_lecon(
    lecon_id: int,
    lecon_data: LeconUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    lecon = db.query(Lecon).filter(Lecon.id == lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon introuvable")

    if lecon_data.titre:   lecon.titre   = lecon_data.titre
    if lecon_data.contenu: lecon.contenu = lecon_data.contenu
    if lecon_data.ordre:   lecon.ordre   = lecon_data.ordre

    db.commit()
    db.refresh(lecon)
    return lecon

@router.delete("/{lecon_id}")
def delete_lecon(
    lecon_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    lecon = db.query(Lecon).filter(Lecon.id == lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon introuvable")
    db.delete(lecon)
    db.commit()
    return {"message": f"Leçon {lecon_id} supprimée"}

# ── Médias ────────────────────────────────────────────────────────────────────

@router.post("/{lecon_id}/medias", response_model=MediaResponse)
def add_media(
    lecon_id: int,
    media_data: MediaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    if media_data.type not in ["image", "video"]:
        raise HTTPException(status_code=400, detail="Type doit être 'image' ou 'video'")

    media = Media(
        lecon_id=lecon_id,
        type=media_data.type,
        url=media_data.url,
        ordre=media_data.ordre
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

@router.delete("/medias/{media_id}")
def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("professeur", "admin"))
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Média introuvable")
    db.delete(media)
    db.commit()
    return {"message": f"Média {media_id} supprimé"}
