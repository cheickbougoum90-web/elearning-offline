from app.schemas.utilisateur import (
    UtilisateurCreate, UtilisateurResponse,
    LoginRequest, TokenResponse
)
from app.schemas.cours import CoursCreate, CoursUpdate, CoursResponse
from app.schemas.lecon import LeconCreate, LeconUpdate, LeconResponse, MediaCreate, MediaResponse
from app.schemas.quiz import QuizCreate, QuizResponse, SoumettreReponse, ResultatQuiz
from app.schemas.progression import ProgressionCreate, ProgressionResponse, ProgressionStats
from app.schemas.avis import AvisCreate, AvisResponse, ClassementProfesseur
