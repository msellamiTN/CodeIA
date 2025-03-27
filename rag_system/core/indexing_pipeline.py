import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_core.documents import Document

from utils.document_processor import DocumentProcessor
from core.elasticsearch_manager import ElasticsearchManager
from config.config import DOCUMENTS_DIR


class IndexingPipeline:
    """Pipeline pour traiter et indexer des documents dans ElasticSearch."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.es_manager = ElasticsearchManager()
    
    def index_file(self, file_path: Union[str, Path]) -> int:
        """Traiter et indexer un fichier unique."""
        file_path = Path(file_path)
        
        print(f"Traitement du fichier: {file_path.name}")
        
        try:
            # Traiter le document
            documents = self.document_processor.load_document(file_path)
            
            # Indexer les documents
            num_indexed = self.es_manager.index_documents(documents)
            
            print(f"Fichier {file_path.name} traité avec succès. {num_indexed} chunks indexés.")
            return num_indexed
            
        except Exception as e:
            print(f"Erreur lors du traitement du fichier {file_path.name}: {str(e)}")
            return 0
    
    def index_directory(self, directory_path: Union[str, Path] = None) -> int:
        """Traiter et indexer tous les documents d'un répertoire."""
        if directory_path is None:
            directory_path = DOCUMENTS_DIR
        
        directory_path = Path(directory_path)
        
        print(f"Traitement du répertoire: {directory_path}")
        
        try:
            # Traiter tous les documents du répertoire
            documents = self.document_processor.process_directory(directory_path)
            
            # Indexer les documents
            num_indexed = self.es_manager.index_documents(documents)
            
            print(f"Répertoire {directory_path} traité avec succès. {num_indexed} chunks indexés.")
            return num_indexed
            
        except Exception as e:
            print(f"Erreur lors du traitement du répertoire {directory_path}: {str(e)}")
            return 0
    
    def clear_index(self):
        """Supprimer tous les documents de l'index."""
        self.es_manager.delete_all_documents()
    
    def get_document_count(self) -> int:
        """Obtenir le nombre de documents indexés."""
        return self.es_manager.get_document_count()
    
    def save_uploaded_file(self, uploaded_file, save_dir: Union[str, Path] = None) -> Optional[Path]:
        """Sauvegarder un fichier téléchargé et l'indexer."""
        if save_dir is None:
            save_dir = DOCUMENTS_DIR
        
        save_dir = Path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            # Construire le chemin de sauvegarde
            file_path = save_dir / uploaded_file.name
            
            # Sauvegarder le fichier
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            print(f"Fichier {uploaded_file.name} sauvegardé avec succès.")
            
            # Indexer le fichier
            self.index_file(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier {uploaded_file.name}: {str(e)}")
            return None 