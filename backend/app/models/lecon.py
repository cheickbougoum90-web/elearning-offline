from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Lecon(Base):
    __tablename__ = "lecons"

    id       = Column(Integer, primary_key=True, index=True)
    titre    = Column(String(200), nullable=False)
    contenu  = Column(Text)
    cours_id = Column(Integer, ForeignKey("cours.id"), nullable=False)
    ordre    = Column(Integer, default=1)

    # Relations
    cours       = relationship("Cours", back_populates="lecons")
    medias      = relationship("Media", back_populates="lecon", cascade="all, delete-orphan")
    quiz        = relationship("Quiz", back_populates="lecon", cascade="all, delete-orphan")
    progressions = relationship("Progression", back_populates="lecon")
