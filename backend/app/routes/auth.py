from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import LoginRequest, TokenResponse
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/login", response_model=TokenResponse)
def login(
    # OAuth2PasswordRequestForm utilise 'username' et 'password'
    # ce qui est compatible avec Swagger UI
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Chercher l'utilisateur par email (username = email dans notre cas)
    user = db.query(Utilisateur).filter(
        Utilisateur.email == form_data.username
    ).first()

    # Vérifier existence + mot de passe
    if not user or not verify_password(form_data.password, user.mot_de_passe):
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
    return {"message": "Déconnexion réussie"}
