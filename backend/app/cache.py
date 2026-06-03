import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Connexion au serveur Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True  # retourne des strings au lieu de bytes
)

def get_cache():
    """Dépendance FastAPI pour accéder à Redis."""
    return redis_client

# ── Helpers ───────────────────────────────────────────────────────────────────

def cache_set(key: str, value: str, expire: int = 600):
    """Stocker une valeur — expire en secondes (défaut 10 min)."""
    redis_client.setex(key, expire, value)

def cache_get(key: str):
    """Récupérer une valeur — retourne None si absente ou expirée."""
    return redis_client.get(key)

def cache_delete(key: str):
    """Supprimer une entrée du cache."""
    redis_client.delete(key)

def cache_delete_pattern(pattern: str):
    """Supprimer toutes les clés correspondant à un pattern.
    Ex: cache_delete_pattern('cours:*') supprime tout le cache des cours.
    """
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
