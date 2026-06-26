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
        if db.query(Utilisateur).count() > 0:
            print("✅ Données déjà présentes — seed ignoré")
            return

        print("🌱 Insertion des données de test...")

        # ── Utilisateurs ─────────────────────────────────────────────────────
        admin = Utilisateur(nom="Administrateur", email="admin@esmt.sn", mot_de_passe=hash_password("admin2026"), role="admin")
        prof1 = Utilisateur(nom="Dr DIAGNE", email="diagne@esmt.sn", mot_de_passe=hash_password("prof2026"), role="professeur")
        prof2 = Utilisateur(nom="Dr FALL", email="fall@esmt.sn", mot_de_passe=hash_password("prof2026"), role="professeur")
        eleve1 = Utilisateur(nom="Cheïck BOUGOUM", email="bougoum@esmt.sn", mot_de_passe=hash_password("eleve2026"), role="eleve")
        eleve2 = Utilisateur(nom="Aminata DIALLO", email="aminata@esmt.sn", mot_de_passe=hash_password("eleve2026"), role="eleve")
        eleve3 = Utilisateur(nom="SISSAO Grace", email="grace@esmt.sn", mot_de_passe=hash_password("eleve2026"), role="eleve")

        db.add_all([admin, prof1, prof2, eleve1, eleve2, eleve3])
        db.flush()

        # ── Cours ─────────────────────────────────────────────────────────────
        cours1 = Cours(titre="Introduction à Python", description="Les bases du langage Python pour la Data Science", prof_id=prof1.id)
        cours2 = Cours(titre="Docker & Conteneurisation", description="Maîtriser Docker et Docker Compose pour le déploiement", prof_id=prof1.id)
        cours3 = Cours(titre="Machine Learning avec Scikit-Learn", description="Algorithmes de ML appliqués aux données réelles", prof_id=prof2.id)
        cours4 = Cours(titre="Base du NoSQL", description="Maîtrise des concepts fondamentaux des bases NoSQL", prof_id=prof2.id)

        db.add_all([cours1, cours2, cours3, cours4])
        db.flush()

        # ── Leçons ────────────────────────────────────────────────────────────
        lecon1 = Lecon(titre="Variables et types de données", contenu="En Python, une variable est créée en lui assignant une valeur. Python est un langage à typage dynamique : le type est déterminé automatiquement. Les types de base sont : int, float, str, bool, list, dict.", cours_id=cours1.id, ordre=1)
        lecon2 = Lecon(titre="Fonctions et modules", contenu="Une fonction se définit avec le mot-clé def. Les modules s'importent avec import. Python dispose d'une bibliothèque standard très riche.", cours_id=cours1.id, ordre=2)
        lecon3 = Lecon(titre="Introduction à Docker", contenu="Docker est une plateforme de conteneurisation. Un conteneur est une unité isolée contenant une application et toutes ses dépendances. La commande docker compose up démarre tous les services définis dans docker-compose.yml.", cours_id=cours2.id, ordre=1)
        lecon4 = Lecon(titre="Docker Compose", contenu="Docker Compose permet d'orchestrer plusieurs conteneurs via un fichier YAML. Chaque service est isolé et peut communiquer avec les autres via un réseau interne.", cours_id=cours2.id, ordre=2)
        lecon5 = Lecon(titre="Introduction aux bases NoSQL", contenu="Les bases de données NoSQL (Not Only SQL) sont apparues pour répondre aux limites des bases relationnelles face aux volumes massifs de données. On distingue quatre familles : orientées documents (MongoDB), colonnes (Cassandra), clé-valeur (Redis) et graphes (Neo4j). Les bases NoSQL privilégient la disponibilité et la tolérance aux pannes selon le théorème CAP.", cours_id=cours4.id, ordre=1)
        lecon6 = Lecon(titre="MongoDB — Concepts Fondamentaux", contenu="MongoDB stocke les données sous forme de documents BSON dans des collections. Concepts clés : Document (unité de stockage JSON), Collection (ensemble de documents), _id (identifiant unique automatique). Avantages : schéma flexible, documents imbriqués, scalabilité horizontale via le sharding, réplication via les Replica Sets.", cours_id=cours4.id, ordre=2)
        lecon7 = Lecon(titre="Comparaison NoSQL vs SQL", contenu="Le choix entre SQL et NoSQL dépend du contexte. SQL est adapté aux données structurées avec relations complexes et cohérence forte (banques, ERP). NoSQL est préféré pour les données volumineuses et hétérogènes (réseaux sociaux, IoT). La règle : schéma fixe et relations fortes → SQL. Données flexibles et volumineuses → NoSQL.", cours_id=cours4.id, ordre=3)

        db.add_all([lecon1, lecon2, lecon3, lecon4, lecon5, lecon6, lecon7])
        db.flush()

        # ── Quiz ──────────────────────────────────────────────────────────────
        quiz1 = Quiz(question="Quel mot-clé permet de définir une fonction en Python ?", lecon_id=lecon2.id)
        quiz2 = Quiz(question="Quelle commande démarre tous les services Docker ?", lecon_id=lecon3.id)
        quiz3 = Quiz(question="Quelles sont les caractéristiques des bases de données NoSQL ?", lecon_id=lecon5.id)
        quiz4 = Quiz(question="Dans quel format MongoDB stocke-t-il ses données ?", lecon_id=lecon6.id)
        quiz5 = Quiz(question="Quel cas d'usage est le plus adapté à une base NoSQL ?", lecon_id=lecon7.id)

        db.add_all([quiz1, quiz2, quiz3, quiz4, quiz5])
        db.flush()

        # ── Réponses ──────────────────────────────────────────────────────────
        db.add_all([
            # Quiz 1 — Python (réponse unique)
            Reponse(quiz_id=quiz1.id, texte="function", est_correcte=False),
            Reponse(quiz_id=quiz1.id, texte="def", est_correcte=True),
            Reponse(quiz_id=quiz1.id, texte="func", est_correcte=False),
            Reponse(quiz_id=quiz1.id, texte="define", est_correcte=False),

            # Quiz 2 — Docker (réponse unique)
            Reponse(quiz_id=quiz2.id, texte="docker run", est_correcte=False),
            Reponse(quiz_id=quiz2.id, texte="docker start", est_correcte=False),
            Reponse(quiz_id=quiz2.id, texte="docker compose up", est_correcte=True),
            Reponse(quiz_id=quiz2.id, texte="docker build", est_correcte=False),

            # Quiz 3 — NoSQL caractéristiques (réponses MULTIPLES)
            Reponse(quiz_id=quiz3.id, texte="Schéma flexible (pas de structure fixe imposée)", est_correcte=True),
            Reponse(quiz_id=quiz3.id, texte="Scalabilité horizontale facilitée", est_correcte=True),
            Reponse(quiz_id=quiz3.id, texte="Garantie ACID stricte sur toutes les opérations", est_correcte=False),
            Reponse(quiz_id=quiz3.id, texte="Adaptées aux données non structurées", est_correcte=True),
            Reponse(quiz_id=quiz3.id, texte="Utilisation obligatoire du langage SQL", est_correcte=False),

            # Quiz 4 — MongoDB format (réponse unique)
            Reponse(quiz_id=quiz4.id, texte="XML", est_correcte=False),
            Reponse(quiz_id=quiz4.id, texte="CSV", est_correcte=False),
            Reponse(quiz_id=quiz4.id, texte="BSON (Binary JSON)", est_correcte=True),
            Reponse(quiz_id=quiz4.id, texte="YAML", est_correcte=False),

            # Quiz 5 — NoSQL vs SQL (réponse unique)
            Reponse(quiz_id=quiz5.id, texte="Une application de réseau social avec des millions d'utilisateurs", est_correcte=True),
            Reponse(quiz_id=quiz5.id, texte="Un système de gestion bancaire nécessitant des transactions ACID strictes", est_correcte=False),
        ])

        db.commit()
        print("✅ Données de test insérées avec succès !")
        print("─────────────────────────────────────")
        print("👤 Admin    : admin@esmt.sn / admin2026")
        print("👨‍🏫 Prof 1   : diagne@esmt.sn / prof2026")
        print("👨‍🏫 Prof 2   : fall@esmt.sn / prof2026")
        print("👨‍🎓 Élève 1  : bougoum@esmt.sn / eleve2026")
        print("👨‍🎓 Élève 2  : aminata@esmt.sn / eleve2026")
        print("👨‍🎓 Élève 3  : grace@esmt.sn / eleve2026")
        print("─────────────────────────────────────")
        print("📚 4 cours, 7 leçons, 5 quiz insérés")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur seed : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
