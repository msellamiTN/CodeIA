#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier les fonctionnalités du système RAG.
Il permet de tester l'indexation, la recherche et la génération de réponses.
"""

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
parent_dir = Path(__file__).resolve().parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from config.config import DATA_DIR, DOCUMENTS_DIR
from core.indexing_pipeline import IndexingPipeline
from core.rag_service import RAGService
from utils.document_processor import DocumentProcessor


def test_elasticsearch_connection():
    """Tester la connexion à ElasticSearch."""
    print("Test de connexion à ElasticSearch...")
    
    from core.elasticsearch_manager import ElasticsearchManager
    
    try:
        es_manager = ElasticsearchManager()
        if es_manager.client.ping():
            print("✅ Connexion à ElasticSearch réussie!")
            return True
        else:
            print("❌ Échec de la connexion à ElasticSearch.")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à ElasticSearch: {str(e)}")
        return False


def test_document_processing():
    """Tester le traitement des documents."""
    print("\nTest de traitement des documents...")
    
    # Créer un document de test
    test_dir = DOCUMENTS_DIR
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = test_dir / "test_document.txt"
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""
        Ceci est un document de test pour le système RAG.
        
        ElasticSearch est un moteur de recherche distribué basé sur Lucene.
        Il est souvent utilisé pour l'indexation et la recherche de documents textuels.
        
        LangChain est une bibliothèque pour construire des applications basées sur des LLM.
        Elle facilite l'intégration de différentes sources de données et de modèles de langage.
        
        Un système RAG (Retrieval Augmented Generation) combine la recherche d'informations et la génération de texte.
        Il utilise des documents récupérés pour enrichir les réponses générées par un modèle de langage.
        """)
    
    try:
        processor = DocumentProcessor()
        documents = processor.load_document(test_file)
        
        print(f"✅ Traitement du document réussi: {len(documents)} chunks créés.")
        return documents
    except Exception as e:
        print(f"❌ Erreur lors du traitement du document: {str(e)}")
        return None


def test_indexing(documents=None):
    """Tester l'indexation des documents."""
    print("\nTest d'indexation...")
    
    if documents is None:
        documents = test_document_processing()
        
    if not documents:
        print("❌ Aucun document à indexer.")
        return False
    
    try:
        pipeline = IndexingPipeline()
        
        # Nettoyer l'index avant le test
        pipeline.clear_index()
        
        # Indexer les documents
        for doc in documents:
            pipeline.es_manager.index_documents([doc])
        
        # Vérifier le nombre de documents indexés
        doc_count = pipeline.get_document_count()
        
        if doc_count > 0:
            print(f"✅ Indexation réussie: {doc_count} documents indexés.")
            return True
        else:
            print("❌ Échec de l'indexation: aucun document indexé.")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'indexation: {str(e)}")
        return False


def test_rag_query():
    """Tester la génération de réponses avec le système RAG."""
    print("\nTest de requête RAG...")
    
    try:
        rag_service = RAGService()
        
        # Requête de test
        query = "Qu'est-ce qu'un système RAG et comment fonctionne-t-il?"
        
        print(f"Question: {query}")
        print("Génération de la réponse...")
        
        # Obtenir une réponse
        response = rag_service.process_query(query)
        
        if response and "answer" in response:
            print("\nRéponse générée:")
            print(f"{response['answer']}")
            
            if response["sources"]:
                print("\nSources:")
                for source in response["sources"]:
                    print(f"- {source}")
            
            print("\n✅ Test de requête RAG réussi!")
            return True
        else:
            print("❌ Échec de la génération de réponse.")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la génération de réponse: {str(e)}")
        return False


def main():
    """Exécuter tous les tests."""
    print("====================================")
    print("  TEST DU SYSTÈME RAG")
    print("====================================\n")
    
    # Test de connexion à ElasticSearch
    if not test_elasticsearch_connection():
        print("\n❌ Tests interrompus: impossible de se connecter à ElasticSearch.")
        print("Assurez-vous qu'ElasticSearch est en cours d'exécution et accessible.")
        return
    
    # Test de traitement des documents
    documents = test_document_processing()
    
    # Test d'indexation
    if not test_indexing(documents):
        print("\n❌ Tests interrompus: échec de l'indexation.")
        return
    
    # Test de requête RAG
    test_rag_query()
    
    print("\n====================================")
    print("  TESTS TERMINÉS")
    print("====================================")


if __name__ == "__main__":
    main() 