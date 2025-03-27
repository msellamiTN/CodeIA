FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration et d'exigences
COPY requirements.txt .
COPY .env.example .env

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Création des répertoires de données
RUN mkdir -p /app/data/documents /app/data/embeddings

# Exposition du port pour Streamlit
EXPOSE 8501

# Commande d'exécution
CMD ["python", "main.py", "run"] 