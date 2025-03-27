@echo off
REM Script de déploiement pour Windows - Système RAG avec ElasticSearch et LangChain

echo [INFO] Vérification des prérequis...

REM Vérifier si Docker est installé
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Docker n'est pas installé ou n'est pas dans le PATH. Veuillez installer Docker avant de continuer.
    exit /b 1
)

REM Vérifier si Docker Compose est installé
where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Docker Compose n'est pas installé ou n'est pas dans le PATH.
    exit /b 1
)

REM Vérifier si le fichier .env existe, sinon le créer à partir du modèle
if not exist .env (
    echo [INFO] Création du fichier .env à partir du modèle .env.example
    copy .env.example .env
    echo [AVERTISSEMENT] Veuillez éditer le fichier .env pour configurer vos propres paramètres.
)

REM Traiter les arguments
set CLEAN_VOLUMES=false
set USE_GPU=false

:parse_args
if "%~1"=="" goto :deploy
if "%~1"=="-c" set CLEAN_VOLUMES=true
if "%~1"=="-g" set USE_GPU=true
if "%~1"=="-v" (
    docker-compose -f docker-compose.yml ps
    exit /b 0
)
if "%~1"=="-h" (
    echo Usage: %0 [-c] [-g] [-v] [-h]
    echo   -c  Nettoyer les volumes avant le déploiement
    echo   -g  Utiliser la configuration GPU
    echo   -v  Afficher l'état des conteneurs en cours d'exécution
    echo   -h  Afficher ce message d'aide
    exit /b 0
)
shift
goto :parse_args

:deploy
REM Définir le fichier de composition Docker
set COMPOSE_FILE=docker-compose.yml
if "%USE_GPU%"=="true" set COMPOSE_FILE=docker-compose.gpu.yml

echo [INFO] Déploiement du système RAG avec le fichier %COMPOSE_FILE%

REM Arrêter les conteneurs existants
echo [INFO] Arrêt des conteneurs existants...
docker-compose -f %COMPOSE_FILE% down

REM Nettoyer les volumes si demandé
if "%CLEAN_VOLUMES%"=="true" (
    echo [INFO] Nettoyage des volumes...
    for /f "tokens=*" %%v in ('docker volume ls -q ^| findstr -i "elasticsearch-data ollama-data"') do (
        docker volume rm %%v
    )
)

REM Démarrer les nouveaux conteneurs
echo [INFO] Démarrage des conteneurs...
docker-compose -f %COMPOSE_FILE% up -d

REM Vérifier l'état des conteneurs
echo [INFO] Vérification de l'état des conteneurs...
timeout /t 5 /nobreak >nul
docker-compose -f %COMPOSE_FILE% ps

echo [INFO] Déploiement terminé!
echo [INFO] L'interface Streamlit est accessible à l'adresse: http://localhost:8501
echo [INFO] Kibana est accessible à l'adresse: http://localhost:5601
echo [INFO] ElasticSearch est accessible à l'adresse: http://localhost:9200

exit /b 0 