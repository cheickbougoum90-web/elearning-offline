from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse
from app.auth import hash_password, require_role

router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])

@router.get("/", response_model=List[UtilisateurResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return db.query(Utilisateur).all()

@router.post("/", response_model=UtilisateurResponse)
def create_user(
    user_data: UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    # Vérifier que l'email n'existe pas déjà
    existing = db.query(Utilisateur).filter(
        Utilisateur.email == user_data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Vérifier que le rôle est valide
    if user_data.role not in ["eleve", "professeur", "admin"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")

    # Créer l'utilisateur avec mot de passe haché
    user = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        mot_de_passe=hash_password(user_data.mot_de_passe),
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UtilisateurResponse)
def update_user(
    user_id: int,
    user_data: UtilisateurCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.nom   = user_data.nom
    user.email = user_data.email
    user.mot_de_passe = hash_password(user_data.mot_de_passe)
    user.role  = user_data.role
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user_id} supprimé"}
