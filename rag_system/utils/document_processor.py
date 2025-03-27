import json
import os
from typing import List, Dict, Any, Union
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader
from langchain_core.documents import Document

from config.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """Classe pour traiter différents types de documents et les préparer pour l'indexation."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
    
    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        """Charge un document à partir du chemin spécifié en fonction de son extension."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._load_pdf(file_path)
        elif extension == '.txt':
            return self._load_text(file_path)
        elif extension == '.json':
            return self._load_json(file_path)
        else:
            raise ValueError(f"Type de fichier non pris en charge: {extension}")
    
    def _load_pdf(self, file_path: Path) -> List[Document]:
        """Charge un document PDF."""
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def _load_text(self, file_path: Path) -> List[Document]:
        """Charge un document texte."""
        loader = TextLoader(str(file_path))
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def _load_json(self, file_path: Path) -> List[Document]:
        """Charge un document JSON."""
        def _extract_content(record: Dict[str, Any], metadata: Dict[str, Any]) -> str:
            # Adaptez cette fonction selon la structure de vos fichiers JSON
            if isinstance(record, dict):
                # Essayez d'extraire un champ de contenu commun, ou convertissez l'ensemble du JSON en texte
                return record.get('content', json.dumps(record))
            return json.dumps(record)
        
        loader = JSONLoader(
            file_path=str(file_path),
            jq_schema=".",
            content_key=None,  # Nous utiliserons une fonction d'extraction personnalisée
            text_content=False,
            json_lines=False,
            content_extractor=_extract_content
        )
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def process_directory(self, directory_path: Union[str, Path]) -> List[Document]:
        """Traite tous les documents pris en charge dans un répertoire."""
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"{directory_path} n'est pas un répertoire valide.")
        
        all_documents = []
        supported_extensions = ['.pdf', '.txt', '.json']
        
        for file_path in directory_path.glob('**/*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    documents = self.load_document(file_path)
                    all_documents.extend(documents)
                    print(f"Traitement réussi: {file_path.name}")
                except Exception as e:
                    print(f"Erreur lors du traitement de {file_path.name}: {str(e)}")
        
        return all_documents 