.PHONY: setup run test deploy-cpu deploy-gpu clean-volumes stop-containers

# Configuration
PYTHON := python
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_FILE := docker-compose.yml
DOCKER_COMPOSE_GPU_FILE := docker-compose.gpu.yml

# Commandes
setup:
	@echo "Installation des dépendances Python..."
	pip install -r requirements.txt
	@echo "Création du fichier .env..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "Installation terminée. N'oubliez pas de configurer votre fichier .env!"

run:
	@echo "Démarrage de l'application Streamlit..."
	$(PYTHON) main.py run

test:
	@echo "Exécution des tests du système..."
	$(PYTHON) test_system.py

deploy-cpu:
	@echo "Déploiement du système RAG (CPU)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "Déploiement terminé. Application accessible à l'adresse http://localhost:8501"

deploy-gpu:
	@echo "Déploiement du système RAG (GPU)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_GPU_FILE) up -d
	@echo "Déploiement terminé. Application accessible à l'adresse http://localhost:8501"

clean-volumes:
	@echo "Nettoyage des volumes Docker..."
	docker volume rm $$(docker volume ls -q | grep -E 'elasticsearch-data|ollama-data') 2>/dev/null || true

stop-containers:
	@echo "Arrêt des conteneurs..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down
	@echo "Conteneurs arrêtés."

help:
	@echo "Commandes disponibles:"
	@echo "  make setup           - Installer les dépendances Python et créer le fichier .env"
	@echo "  make run             - Démarrer l'application Streamlit localement"
	@echo "  make test            - Exécuter les tests du système"
	@echo "  make deploy-cpu      - Déployer le système avec Docker (CPU)"
	@echo "  make deploy-gpu      - Déployer le système avec Docker (GPU)"
	@echo "  make clean-volumes   - Nettoyer les volumes Docker"
	@echo "  make stop-containers - Arrêter les conteneurs Docker"
	@echo "  make help            - Afficher ce message d'aide"

# Par défaut, afficher l'aide
default: help 