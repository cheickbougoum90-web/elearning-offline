from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import LoginRequest, TokenResponse
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Chercher l'utilisateur par email
    user = db.query(Utilisateur).filter(
        Utilisateur.email == request.email
    ).first()

    # Vérifier existence + mot de passe
    if not user or not verify_password(request.mot_de_passe, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Générer le token JWT
    token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        nom=user.nom
    )

@router.post("/logout")
def logout():
    # Côté serveur stateless — le client supprime son token
    return {"message": "Déconnexion réussie"}
