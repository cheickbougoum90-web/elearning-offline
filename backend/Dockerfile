FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier et installer les dépendances d'abord
# (optimisation cache Docker — si requirements.txt ne change pas,
#  cette couche n'est pas reconstruite)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Exposer le port FastAPI
EXPOSE 8000

# Démarrer le serveur avec rechargement automatique (dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
