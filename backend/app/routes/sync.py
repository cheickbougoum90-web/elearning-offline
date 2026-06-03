from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.progression import Progression
from app.auth import require_role

router = APIRouter(prefix="/api/sync", tags=["Synchronisation"])

@router.post("/")
def sync_data(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """Marquer toutes les progressions locales comme synchronisées."""
    non_synced = db.query(Progression).filter(
        Progression.synced == False
    ).all()

    count = len(non_synced)
    for prog in non_synced:
        prog.synced = True

    db.commit()

    return {
        "message": f"Synchronisation réussie",
        "donnees_synchronisees": count,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
def sync_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """Voir combien de données attendent d'être synchronisées."""
    en_attente = db.query(Progression).filter(
        Progression.synced == False
    ).count()

    total = db.query(Progression).count()

    return {
        "total_progressions": total,
        "en_attente_sync": en_attente,
        "synchronisees": total - en_attente,
        "statut": "✅ À jour" if en_attente == 0 else f"⚠️ {en_attente} éléments en attente"
    }
