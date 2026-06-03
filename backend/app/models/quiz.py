from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Quiz(Base):
    __tablename__ = "quiz"

    id       = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    lecon_id = Column(Integer, ForeignKey("lecons.id"), nullable=False)

    # Relations
    lecon    = relationship("Lecon", back_populates="quiz")
    reponses = relationship("Reponse", back_populates="quiz", cascade="all, delete-orphan")
