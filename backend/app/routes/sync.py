from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import os

from app.database import get_db
from app.models.progression import Progression
from app.models.avis import Avis
from app.models.cours import Cours
from app.auth import require_role, create_access_token

router = APIRouter(prefix="/api/sync", tags=["Synchronisation"])

CLOUD_URL = os.getenv("CLOUD_SERVER_URL", "")

def get_cloud_token() -> str:
    return create_access_token(data={"sub": "1", "role": "admin"})

@router.post("/receive/progressions")
def receive_progressions(payload: dict, db: Session = Depends(get_db)):
    from app.models.lecon import Lecon
    from app.models.utilisateur import Utilisateur
    inserted = 0
    updated  = 0
    skipped  = 0
    lecons_ids = {l.id for l in db.query(Lecon.id).all()}
    users_ids  = {u.id for u in db.query(Utilisateur.id).all()}
    for p in payload.get("progressions", []):
        if p["lecon_id"] not in lecons_ids or p["user_id"] not in users_ids:
            skipped += 1
            continue
        existing = db.query(Progression).filter(
            Progression.user_id  == p["user_id"],
            Progression.lecon_id == p["lecon_id"]
        ).first()
        if existing:
            if p.get("updated_at", "") > str(existing.updated_at):
                existing.statut = p["statut"]
                existing.score  = p["score"]
                existing.synced = True
                updated += 1
        else:
            db.add(Progression(
                user_id  = p["user_id"],
                lecon_id = p["lecon_id"],
                statut   = p["statut"],
                score    = p["score"],
                synced   = True
            ))
            inserted += 1
    db.commit()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}

@router.post("/receive/avis")
def receive_avis(payload: dict, db: Session = Depends(get_db)):
    inserted = 0
    for a in payload.get("avis", []):
        existing = db.query(Avis).filter(
            Avis.user_id  == a["user_id"],
            Avis.cours_id == a["cours_id"]
        ).first()
        if not existing:
            db.add(Avis(
                user_id     = a["user_id"],
                cours_id    = a["cours_id"],
                note        = a["note"],
                commentaire = a.get("commentaire", "")
            ))
            inserted += 1
    db.commit()
    return {"inserted": inserted}

@router.post("/")
async def sync_data(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    if not CLOUD_URL:
        return {
            "success": False,
            "message": "URL du serveur cloud non configurée",
            "timestamp": datetime.utcnow().isoformat()
        }

    resultats = {
        "push_progressions": 0,
        "push_avis": 0,
        "pull_cours": 0,
        "errors": []
    }

    token   = get_cloud_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as client:

        # PHASE 1 — PUSH progressions
        try:
            non_synced = db.query(Progression).filter(Progression.synced == False).all()
            if non_synced:
                payload = {"progressions": [
                    {
                        "user_id":    p.user_id,
                        "lecon_id":   p.lecon_id,
                        "statut":     p.statut,
                        "score":      p.score,
                        "updated_at": str(p.updated_at)
                    }
                    for p in non_synced
                ]}
                res = await client.post(
                    f"{CLOUD_URL}/api/sync/receive/progressions",
                    json=payload, headers=headers
                )
                res.raise_for_status()
                for p in non_synced:
                    p.synced = True
                db.commit()
                resultats["push_progressions"] = len(non_synced)
        except Exception as e:
            resultats["errors"].append(f"PUSH progressions: {str(e)}")

        # PHASE 2 — PUSH avis
        try:
            avis_list = db.query(Avis).all()
            if avis_list:
                payload = {"avis": [
                    {
                        "user_id":    a.user_id,
                        "cours_id":   a.cours_id,
                        "note":       a.note,
                        "commentaire": a.commentaire or ""
                    }
                    for a in avis_list
                ]}
                res = await client.post(
                    f"{CLOUD_URL}/api/sync/receive/avis",
                    json=payload, headers=headers
                )
                res.raise_for_status()
                resultats["push_avis"] = len(avis_list)
        except Exception as e:
            resultats["errors"].append(f"PUSH avis: {str(e)}")

        # PHASE 3 — PULL cours depuis cloud
        try:
            res = await client.get(f"{CLOUD_URL}/api/cours/", headers=headers)
            res.raise_for_status()
            cours_cloud = res.json()
            ids_locaux  = {c.id for c in db.query(Cours.id).all()}
            nouveaux    = 0
            for c in cours_cloud:
                if c["id"] not in ids_locaux:
                    db.add(Cours(
                        id            = c["id"],
                        titre         = c["titre"],
                        description   = c.get("description", ""),
                        prof_id       = c["prof_id"],
                        moyenne_notes = c.get("moyenne_notes", 0)
                    ))
                    nouveaux += 1
            db.commit()
            resultats["pull_cours"] = nouveaux
        except Exception as e:
            resultats["errors"].append(f"PULL cours: {str(e)}")

    success = len(resultats["errors"]) == 0
    return {
        "success": success,
        "message": "Synchronisation réussie" if success else "Synchronisation partielle",
        "details": resultats,
        "donnees_synchronisees": resultats["push_progressions"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def sync_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    en_attente = db.query(Progression).filter(Progression.synced == False).count()
    total      = db.query(Progression).count()

    cloud_accessible = False
    if CLOUD_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{CLOUD_URL}/")
                cloud_accessible = res.status_code == 200
        except:
            cloud_accessible = False

    return {
        "total_progressions": total,
        "en_attente_sync":    en_attente,
        "synchronisees":      total - en_attente,
        "cloud_url":          CLOUD_URL,
        "cloud_accessible":   cloud_accessible,
        "statut": "✅ À jour" if en_attente == 0 else f"⚠️ {en_attente} éléments en attente"
    }
