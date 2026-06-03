from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Media(Base):
    __tablename__ = "medias"

    id       = Column(Integer, primary_key=True, index=True)
    lecon_id = Column(Integer, ForeignKey("lecons.id"), nullable=False)
    type     = Column(String(10), nullable=False)  # image | video
    url      = Column(Text, nullable=False)
    ordre    = Column(Integer, default=1)

    # Relations
    lecon = relationship("Lecon", back_populates="medias")
