import os
import argparse
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def run_streamlit_app():
    """Lancer l'application Streamlit."""
    app_path = Path(__file__).resolve().parent / "app" / "streamlit_app.py"
    subprocess.run(["streamlit", "run", str(app_path)])


def index_documents(directory_path=None):
    """Indexer les documents dans le répertoire spécifié."""
    from core.indexing_pipeline import IndexingPipeline
    
    pipeline = IndexingPipeline()
    
    if directory_path:
        num_indexed = pipeline.index_directory(directory_path)
    else:
        num_indexed = pipeline.index_directory()
    
    print(f"Indexation terminée. {num_indexed} chunks indexés.")


def clear_index():
    """Supprimer tous les documents de l'index."""
    from core.indexing_pipeline import IndexingPipeline
    
    pipeline = IndexingPipeline()
    pipeline.clear_index()
    print("Index effacé avec succès.")


def main():
    parser = argparse.ArgumentParser(description="Système RAG avec ElasticSearch et LangChain")
    
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")
    
    # Commande run
    run_parser = subparsers.add_parser("run", help="Lancer l'application Streamlit")
    
    # Commande index
    index_parser = subparsers.add_parser("index", help="Indexer des documents")
    index_parser.add_argument(
        "--directory", "-d", help="Chemin du répertoire à indexer"
    )
    
    # Commande clear
    clear_parser = subparsers.add_parser("clear", help="Effacer l'index")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_streamlit_app()
    elif args.command == "index":
        index_documents(args.directory)
    elif args.command == "clear":
        clear_index()
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 