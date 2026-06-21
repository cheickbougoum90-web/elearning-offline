from sqlalchemy import Column, Integer, SmallInteger, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Avis(Base):
    __tablename__ = "avis"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    cours_id    = Column(Integer, ForeignKey("cours.id"), nullable=False)
    note        = Column(SmallInteger, nullable=False)
    commentaire = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # Un élève ne peut noter un cours qu'une seule fois
    # La note doit être entre 1 et 5
    __table_args__ = (
        UniqueConstraint("user_id", "cours_id", name="uq_user_cours"),
        CheckConstraint("note >= 1 AND note <= 5", name="check_note_range"),
    )

    # Relations
    utilisateur = relationship("Utilisateur", back_populates="avis")
    cours       = relationship("Cours", back_populates="avis")
