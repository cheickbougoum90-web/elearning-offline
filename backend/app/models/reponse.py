from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Reponse(Base):
    __tablename__ = "reponses"

    id           = Column(Integer, primary_key=True, index=True)
    quiz_id      = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    texte        = Column(Text, nullable=False)
    est_correcte = Column(Boolean, default=False)

    # Relations
    quiz = relationship("Quiz", back_populates="reponses")
