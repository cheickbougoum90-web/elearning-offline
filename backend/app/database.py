from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

# Construction de l'URL de connexion PostgreSQL
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

# Moteur SQLAlchemy — pool_pre_ping vérifie la connexion avant chaque requête
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous les modèles
class Base(DeclarativeBase):
    pass

# Dépendance FastAPI — fournit une session BDD à chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
