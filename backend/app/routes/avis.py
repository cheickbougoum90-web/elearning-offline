from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.avis import Avis
from app.models.cours import Cours
from app.models.progression import Progression
from app.models.lecon import Lecon
from app.models.utilisateur import Utilisateur
from app.schemas.avis import AvisCreate, AvisResponse, ClassementProfesseur
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/avis", tags=["Avis"])

@router.post("/", response_model=AvisResponse)
def create_avis(
    avis_data: AvisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("eleve"))
):
    # Vérifier que le cours existe
    cours = db.query(Cours).filter(Cours.id == avis_data.cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    # Vérifier que toutes les leçons sont terminées
    total_lecons = db.query(Lecon).filter(Lecon.cours_id == avis_data.cours_id).count()
    lecons_terminees = db.query(Progression).join(Lecon).filter(
        Progression.user_id == current_user.id,
        Progression.statut == "termine",
        Lecon.cours_id == avis_data.cours_id
    ).count()

    if lecons_terminees < total_lecons:
        raise HTTPException(
            status_code=400,
            detail=f"Vous devez terminer toutes les leçons avant de noter ({lecons_terminees}/{total_lecons} terminées)"
        )

    # Vérifier que l'élève n'a pas déjà noté
    existing = db.query(Avis).filter(
        Avis.user_id == current_user.id,
        Avis.cours_id == avis_data.cours_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà noté ce cours")

    # Créer l'avis
    avis = Avis(
        user_id=current_user.id,
        cours_id=avis_data.cours_id,
        note=avis_data.note,
        commentaire=avis_data.commentaire
    )
    db.add(avis)
    db.flush()

    # Recalculer la moyenne du cours
    moyenne = db.query(func.avg(Avis.note)).filter(
        Avis.cours_id == avis_data.cours_id
    ).scalar()
    cours.moyenne_notes = round(float(moyenne), 2)

    db.commit()
    db.refresh(avis)
    return avis

@router.get("/cours/{cours_id}", response_model=List[AvisResponse])
def get_avis_cours(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Avis).filter(Avis.cours_id == cours_id).all()

@router.get("/classement/profs", response_model=List[ClassementProfesseur])
def get_classement_profs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resultats = db.query(
        Utilisateur.id.label("prof_id"),
        Utilisateur.nom.label("nom"),
        func.count(Cours.id.distinct()).label("nombre_cours"),
        func.count(Avis.id).label("nombre_avis"),
        func.coalesce(func.avg(Avis.note), 0).label("moyenne")
    ).join(Cours, Cours.prof_id == Utilisateur.id)\
     .outerjoin(Avis, Avis.cours_id == Cours.id)\
     .filter(Utilisateur.role == "professeur")\
     .group_by(Utilisateur.id, Utilisateur.nom)\
     .order_by(func.coalesce(func.avg(Avis.note), 0).desc())\
     .all()

    return [
        ClassementProfesseur(
            prof_id=r.prof_id,
            nom=r.nom,
            nombre_cours=r.nombre_cours,
            nombre_avis=r.nombre_avis,
            moyenne=round(float(r.moyenne), 2)
        ) for r in resultats
    ]
