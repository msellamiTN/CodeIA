#!/bin/bash

# Script de déploiement pour le système RAG avec ElasticSearch et LangChain

# Couleurs pour une meilleure lisibilité
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages d'information
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Fonction pour afficher les avertissements
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Fonction pour afficher les erreurs
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Veuillez installer Docker avant de continuer."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer."
    exit 1
fi

# Vérifier si le fichier .env existe, sinon le créer à partir du modèle
if [ ! -f .env ]; then
    info "Création du fichier .env à partir du modèle .env.example"
    cp .env.example .env
    warning "Veuillez éditer le fichier .env pour configurer vos propres paramètres."
fi

# Fonction pour déployer le système
deploy() {
    local compose_file=$1
    
    info "Déploiement du système RAG avec le fichier $compose_file"
    
    # Arrêter les conteneurs existants
    info "Arrêt des conteneurs existants..."
    docker-compose -f $compose_file down
    
    # Nettoyer les volumes si demandé
    if [ "$CLEAN_VOLUMES" = true ]; then
        info "Nettoyage des volumes..."
        docker volume rm $(docker volume ls -q | grep -E 'elasticsearch-data|ollama-data') 2>/dev/null || true
    fi
    
    # Démarrer les nouveaux conteneurs
    info "Démarrage des conteneurs..."
    docker-compose -f $compose_file up -d
    
    # Vérifier l'état des conteneurs
    info "Vérification de l'état des conteneurs..."
    sleep 5
    docker-compose -f $compose_file ps
    
    info "Déploiement terminé!"
    info "L'interface Streamlit est accessible à l'adresse: http://localhost:8501"
    info "Kibana est accessible à l'adresse: http://localhost:5601"
    info "ElasticSearch est accessible à l'adresse: http://localhost:9200"
}

# Traiter les arguments de ligne de commande
CLEAN_VOLUMES=false
USE_GPU=false

while getopts "cgvh" opt; do
    case $opt in
        c)
            CLEAN_VOLUMES=true
            ;;
        g)
            USE_GPU=true
            ;;
        v)
            docker-compose -f docker-compose.yml ps
            exit 0
            ;;
        h|*)
            echo "Usage: $0 [-c] [-g] [-v] [-h]"
            echo "  -c  Nettoyer les volumes avant le déploiement"
            echo "  -g  Utiliser la configuration GPU"
            echo "  -v  Afficher l'état des conteneurs en cours d'exécution"
            echo "  -h  Afficher ce message d'aide"
            exit 0
            ;;
    esac
done

# Choisir le fichier de configuration Docker Compose en fonction des options
if [ "$USE_GPU" = true ]; then
    deploy "docker-compose.gpu.yml"
else
    deploy "docker-compose.yml"
fi

exit 0 