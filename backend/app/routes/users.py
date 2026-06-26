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

@router.post("/{user_id}/impersonate")
def impersonate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """Génère un token JWT pour se connecter en tant qu'un autre utilisateur.
    Réservé à l'admin. Le token généré garde une trace de l'admin d'origine
    via le champ 'impersonated_by' pour la traçabilité."""
    from app.auth import create_access_token

    target = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if target.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Impossible de se connecter en tant qu'un autre administrateur"
        )

    token = create_access_token(data={
        "sub": str(target.id),
        "role": target.role,
        "impersonated_by": str(current_user.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": target.id,
        "role": target.role,
        "nom": target.nom,
        "impersonated_by_nom": current_user.nom
    }

@router.post("/stop-impersonation")
def stop_impersonation(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin", "professeur", "eleve"))
):
    """Permet de revenir au compte admin d'origine après une impersonation.
    Nécessite que le frontend ait conservé le token admin original."""
    return {"message": "Utilisez le token admin sauvegardé côté client pour revenir."}

@router.get("/all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """Retourne tous les utilisateurs — utilisé pour la sync PULL.
    Ne retourne jamais les mots de passe."""
    users = db.query(Utilisateur).all()
    return [
        {
            "id":    u.id,
            "nom":   u.nom,
            "email": u.email,
            "role":  u.role
        }
        for u in users
    ]
