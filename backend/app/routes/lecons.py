from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.lecon import Lecon
from app.models.cours import Cours
from app.models.media import Media
from app.schemas.lecon import LeconCreate, LeconUpdate, LeconResponse, MediaCreate, MediaResponse
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/lecons", tags=["Leçons"])

def _verifier_proprietaire_cours(cours_id: int, current_user, db: Session):
    """Vérifie que l'utilisateur est admin ou propriétaire du cours.
    Lève une exception 403/404 sinon."""
    cours = db.query(Cours).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    if current_user.role != "admin" and cours.prof_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que les leçons de vos propres cours"
        )
    return cours

def _verifier_proprietaire_lecon(lecon: Lecon, current_user, db: Session):
    """Vérifie que l'utilisateur est admin ou propriétaire du cours
    auquel appartient cette leçon."""
    if current_user.role == "admin":
        return
    cours = db.query(Cours).filter(Cours.id == lecon.cours_id).first()
    if not cours or cours.prof_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez gérer que les leçons de vos propres cours"
        )

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
    _verifier_proprietaire_cours(lecon_data.cours_id, current_user, db)

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

    _verifier_proprietaire_lecon(lecon, current_user, db)

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

    _verifier_proprietaire_lecon(lecon, current_user, db)

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
    lecon = db.query(Lecon).filter(Lecon.id == lecon_id).first()
    if not lecon:
        raise HTTPException(status_code=404, detail="Leçon introuvable")

    _verifier_proprietaire_lecon(lecon, current_user, db)

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

    lecon = db.query(Lecon).filter(Lecon.id == media.lecon_id).first()
    if lecon:
        _verifier_proprietaire_lecon(lecon, current_user, db)

    db.delete(media)
    db.commit()
    return {"message": f"Média {media_id} supprimé"}

@router.get("/all")
def get_all_lecons(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Retourne toutes les leçons — utilisé pour la sync PULL."""
    lecons = db.query(Lecon).order_by(Lecon.cours_id, Lecon.ordre).all()
    return [
        {
            "id":       l.id,
            "titre":    l.titre,
            "contenu":  l.contenu,
            "cours_id": l.cours_id,
            "ordre":    l.ordre
        }
        for l in lecons
    ]
