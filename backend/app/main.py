from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routes import auth, users, cours, lecons, quiz, progression, avis, sync

# ── Créer toutes les tables au démarrage ──────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Application FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Plateforme E-learning Offline-First",
    description="API REST pour la plateforme e-learning — ESMT Dakar — Systèmes Distribués",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS — autoriser le frontend à appeler le backend ─────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # en prod : remplacer par l'URL du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inclure toutes les routes ─────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cours.router)
app.include_router(lecons.router)
app.include_router(quiz.router)
app.include_router(progression.router)
app.include_router(avis.router)
app.include_router(sync.router)

# ── Route de santé ────────────────────────────────────────────────────────────
@app.get("/", tags=["Santé"])
def health_check():
    return {
        "status": "✅ API opérationnelle",
        "projet": "E-learning Offline-First",
        "version": "1.0.0",
        "docs": "/docs"
    }
# ── Seed données de test au premier lancement ─────────────────────────────────
from app.seed import seed
seed()
