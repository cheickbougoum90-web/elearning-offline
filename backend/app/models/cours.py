from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Cours(Base):
    __tablename__ = "cours"

    id            = Column(Integer, primary_key=True, index=True)
    titre         = Column(String(200), nullable=False)
    description   = Column(Text)
    prof_id       = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    moyenne_notes = Column(Float, default=0.0)
    archive       = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    professeur = relationship("Utilisateur", back_populates="cours")
    lecons     = relationship("Lecon", back_populates="cours", cascade="all, delete-orphan")
    avis       = relationship("Avis", back_populates="cours", cascade="all, delete-orphan")
