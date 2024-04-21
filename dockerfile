# Utilisez une image de base Python
FROM python:3.12.2

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de dépendances et installez les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de l'application dans le conteneur
COPY . .

# Exécutez l'application
CMD [ "python", "./requets_github.py" ]