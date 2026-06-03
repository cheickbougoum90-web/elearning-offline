from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id         = Column(Integer, primary_key=True, index=True)
    nom        = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role       = Column(String(20), nullable=False)  # eleve | professeur | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    cours      = relationship("Cours", back_populates="professeur")
    progressions = relationship("Progression", back_populates="utilisateur")
    avis       = relationship("Avis", back_populates="utilisateur")
