# Système RAG avec ElasticSearch et LangChain

Ce projet implémente un système de Retrieval Augmented Generation (RAG) utilisant ElasticSearch comme base de données vectorielle, LangChain pour le traitement et l'orchestration, et Streamlit pour l'interface utilisateur.

## Fonctionnalités

- 📄 Pipeline pour collecter, traiter et indexer des documents (JSON/PDF/TXT)
- 🔍 Recherche sémantique avec ElasticSearch et embeddings
- 🤖 Service de question-réponse utilisant Gemini API ou Ollama local
- 🖥️ Interface utilisateur Streamlit pour télécharger des documents et poser des questions
- 🐳 Déploiement Docker avec support GPU possible

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- Clé API Gemini (si vous utilisez le modèle Gemini)
- Ollama installé localement (si vous utilisez Ollama)

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone <URL_DU_REPO>
   cd rag_system
   ```

2. Installez les dépendances Python :
   ```bash
   # Sur Linux/macOS
   make setup
   
   # OU manuellement
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. Configurez vos variables d'environnement dans le fichier `.env` :
   - Définissez `GEMINI_API_KEY` si vous utilisez Gemini
   - Ou configurez `OLLAMA_URL` si vous utilisez Ollama

## Test du système

Vous pouvez tester le système avant de le déployer complètement :

```bash
# Sur Linux/macOS
make test

# Sur Windows ou manuellement
python test_system.py
```

Ce test vérifie la connexion à ElasticSearch, le traitement des documents et la génération de réponses.

## Déploiement

### Avec Docker (recommandé)

Vous pouvez déployer l'ensemble du système avec Docker Compose :

```bash
# Sur Linux/macOS avec Make
make deploy-cpu   # Version CPU
make deploy-gpu   # Version avec support GPU

# Sur Windows
deploy.bat        # Version CPU
deploy.bat -g     # Version avec support GPU

# OU manuellement
docker-compose up -d                  # Version CPU
docker-compose -f docker-compose.gpu.yml up -d  # Version avec support GPU
```

L'application sera accessible à l'adresse : http://localhost:8501

### Sans Docker

Pour exécuter l'application sans Docker, vous devez d'abord démarrer ElasticSearch séparément :

1. Téléchargez et installez ElasticSearch 8.10.0
2. Démarrez ElasticSearch
3. Lancez l'application Streamlit :

```bash
# Sur Linux/macOS
make run

# Sur Windows ou manuellement
python main.py run
```

## Utilisation

### Interface utilisateur Streamlit

Accédez à http://localhost:8501 pour utiliser l'interface Streamlit.

- **Téléchargement de documents** : Utilisez la colonne de droite pour télécharger des fichiers PDF, TXT ou JSON.
- **Poser des questions** : Entrez votre question dans la zone de chat et recevez une réponse générée à partir des documents pertinents.
- **Voir les sources** : Les sources utilisées pour générer la réponse sont affichées en dessous de celle-ci.

### Commandes en ligne

Vous pouvez également utiliser des commandes pour interagir avec le système :

```bash
# Indexer des documents
python main.py index --directory /chemin/vers/vos/documents

# Effacer l'index
python main.py clear
```

## Arrêt et nettoyage

```bash
# Sur Linux/macOS avec Make
make stop-containers  # Arrêter les conteneurs
make clean-volumes    # Nettoyer les volumes

# Sur Windows
deploy.bat -v         # Voir l'état des conteneurs
docker-compose down   # Arrêter les conteneurs
```

## Structure du projet

```
rag_system/
│
├── app/                  # Interface utilisateur
│   └── streamlit_app.py  # Application Streamlit
│
├── config/               # Configuration
│   └── config.py         # Configuration du système
│
├── core/                 # Logique principale
│   ├── elasticsearch_manager.py  # Gestion d'ElasticSearch
│   ├── indexing_pipeline.py      # Pipeline d'indexation
│   ├── llm_service.py            # Service LLM
│   └── rag_service.py            # Service RAG principal
│
├── data/                 # Données
│   ├── documents/        # Documents à indexer
│   └── embeddings/       # Embeddings générés
│
├── utils/                # Utilitaires
│   └── document_processor.py  # Traitement des documents
│
├── .env.example          # Exemple de fichier .env
├── deploy.bat            # Script de déploiement Windows
├── deploy.sh             # Script de déploiement Unix
├── docker-compose.yml    # Configuration Docker Compose (CPU)
├── docker-compose.gpu.yml # Configuration Docker Compose (GPU)
├── Dockerfile            # Configuration de l'image Docker
├── Makefile              # Commandes Make
├── main.py               # Point d'entrée de l'application
├── test_system.py        # Tests du système
├── README.md             # Documentation
└── requirements.txt      # Dépendances Python
```

## Personnalisation

- **Modèle d'embedding** : Modifiez la variable `EMBEDDING_MODEL` dans le fichier `.env` pour utiliser un modèle d'embedding différent.
- **Fournisseur LLM** : Choisissez entre `gemini` et `ollama` en modifiant la variable `LLM_PROVIDER`.
- **Configuration ElasticSearch** : Modifiez les paramètres d'ElasticSearch dans le fichier `docker-compose.yml`.

## Résolution des problèmes

- **Erreur de connexion à ElasticSearch** : Vérifiez que ElasticSearch est bien démarré et accessible à l'adresse http://localhost:9200.
- **Problème avec les embeddings** : Assurez-vous que le modèle d'embedding spécifié est disponible et que vous avez une connexion Internet active pour le télécharger.
- **Erreur avec Gemini API** : Vérifiez que votre clé API Gemini est correctement configurée dans le fichier `.env`.
- **Problème avec Ollama** : Assurez-vous qu'Ollama est en cours d'exécution et accessible à l'URL spécifiée.

## Licence

Ce projet est sous licence MIT. 