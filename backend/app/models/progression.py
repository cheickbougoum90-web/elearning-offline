from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Progression(Base):
    __tablename__ = "progressions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    lecon_id   = Column(Integer, ForeignKey("lecons.id"), nullable=False)
    statut     = Column(String(20), default="en_cours")  # en_cours | termine
    score      = Column(Float, default=0.0)
    synced     = Column(Boolean, default=False)  # clé offline
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Contrainte : un élève ne peut avoir qu'une progression par leçon
    __table_args__ = (UniqueConstraint("user_id", "lecon_id", name="uq_user_lecon"),)

    # Relations
    utilisateur = relationship("Utilisateur", back_populates="progressions")
    lecon       = relationship("Lecon", back_populates="progressions")
