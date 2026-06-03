from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.models.cours import Cours
from app.models.lecon import Lecon
from app.models.quiz import Quiz
from app.models.reponse import Reponse
from app.auth import hash_password

def seed():
    db = SessionLocal()

    try:
        # Vérifier si des données existent déjà
        if db.query(Utilisateur).count() > 0:
            print("✅ Données déjà présentes — seed ignoré")
            return

        print("🌱 Insertion des données de test...")

        # ── Utilisateurs ──────────────────────────────────────────────────────
        admin = Utilisateur(
            nom="Administrateur",
            email="admin@esmt.sn",
            mot_de_passe=hash_password("admin2026"),
            role="admin"
        )
        prof1 = Utilisateur(
            nom="Dr DIAGNE",
            email="diagne@esmt.sn",
            mot_de_passe=hash_password("prof2026"),
            role="professeur"
        )
        prof2 = Utilisateur(
            nom="Dr FALL",
            email="fall@esmt.sn",
            mot_de_passe=hash_password("prof2026"),
            role="professeur"
        )
        eleve1 = Utilisateur(
            nom="Cheïck BOUGOUM",
            email="bougoum@esmt.sn",
            mot_de_passe=hash_password("eleve2026"),
            role="eleve"
        )
        eleve2 = Utilisateur(
            nom="Aminata DIALLO",
            email="aminata@esmt.sn",
            mot_de_passe=hash_password("eleve2026"),
            role="eleve"
        )

        db.add_all([admin, prof1, prof2, eleve1, eleve2])
        db.flush()

        # ── Cours ─────────────────────────────────────────────────────────────
        cours1 = Cours(
            titre="Introduction à Python",
            description="Les bases du langage Python pour la Data Science",
            prof_id=prof1.id
        )
        cours2 = Cours(
            titre="Docker & Conteneurisation",
            description="Maîtriser Docker et Docker Compose pour le déploiement",
            prof_id=prof1.id
        )
        cours3 = Cours(
            titre="Machine Learning avec Scikit-Learn",
            description="Algorithmes de ML appliqués aux données réelles",
            prof_id=prof2.id
        )

        db.add_all([cours1, cours2, cours3])
        db.flush()

        # ── Leçons ────────────────────────────────────────────────────────────
        lecon1 = Lecon(
            titre="Variables et types de données",
            contenu="En Python, une variable est créée en lui assignant une valeur. Python est un langage à typage dynamique : le type est déterminé automatiquement. Les types de base sont : int, float, str, bool, list, dict.",
            cours_id=cours1.id,
            ordre=1
        )
        lecon2 = Lecon(
            titre="Fonctions et modules",
            contenu="Une fonction se définit avec le mot-clé def. Les modules s'importent avec import. Python dispose d'une bibliothèque standard très riche.",
            cours_id=cours1.id,
            ordre=2
        )
        lecon3 = Lecon(
            titre="Introduction à Docker",
            contenu="Docker est une plateforme de conteneurisation. Un conteneur est une unité isolée contenant une application et toutes ses dépendances. La commande docker compose up démarre tous les services définis dans docker-compose.yml.",
            cours_id=cours2.id,
            ordre=1
        )
        lecon4 = Lecon(
            titre="Docker Compose",
            contenu="Docker Compose permet d'orchestrer plusieurs conteneurs via un fichier YAML. Chaque service est isolé et peut communiquer avec les autres via un réseau interne.",
            cours_id=cours2.id,
            ordre=2
        )

        db.add_all([lecon1, lecon2, lecon3, lecon4])
        db.flush()

        # ── Quiz ──────────────────────────────────────────────────────────────
        quiz1 = Quiz(question="Quel mot-clé permet de définir une fonction en Python ?", lecon_id=lecon2.id)
        quiz2 = Quiz(question="Quelle commande démarre tous les services Docker ?", lecon_id=lecon3.id)

        db.add_all([quiz1, quiz2])
        db.flush()

        # ── Réponses ──────────────────────────────────────────────────────────
        db.add_all([
            Reponse(quiz_id=quiz1.id, texte="function",  est_correcte=False),
            Reponse(quiz_id=quiz1.id, texte="def",       est_correcte=True),
            Reponse(quiz_id=quiz1.id, texte="func",      est_correcte=False),
            Reponse(quiz_id=quiz1.id, texte="define",    est_correcte=False),

            Reponse(quiz_id=quiz2.id, texte="docker run",         est_correcte=False),
            Reponse(quiz_id=quiz2.id, texte="docker start",       est_correcte=False),
            Reponse(quiz_id=quiz2.id, texte="docker compose up",  est_correcte=True),
            Reponse(quiz_id=quiz2.id, texte="docker build",       est_correcte=False),
        ])

        db.commit()
        print("✅ Données de test insérées avec succès !")
        print("─────────────────────────────────────")
        print("👤 Admin    : admin@esmt.sn / admin2026")
        print("👨‍🏫 Prof 1   : diagne@esmt.sn / prof2026")
        print("👨‍🏫 Prof 2   : fall@esmt.sn / prof2026")
        print("👨‍🎓 Élève 1  : bougoum@esmt.sn / eleve2026")
        print("👨‍🎓 Élève 2  : aminata@esmt.sn / eleve2026")
        print("─────────────────────────────────────")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur seed : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
