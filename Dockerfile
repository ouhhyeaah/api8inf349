# Utiliser l'image Python 3.12 officielle comme base
FROM python:3.12

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copier le code source dans le conteneur
COPY . .

# Définir les variables d'environnement par défaut
ENV REDIS_URL $REDIS_URL
ENV DB_HOST $DB_HOST
ENV DB_USER $DB_USER
ENV DB_PASSWORD $DB_PASSWORD
ENV DB_PORT $DB_PORT
ENV DB_NAME $DB_NAME

# Exposer le port 5000 sur lequel l'application Flask s'exécute
EXPOSE 5000
# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]
