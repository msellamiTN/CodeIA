from typing import List, Dict, Any, Optional

from core.elasticsearch_manager import ElasticsearchManager
from core.llm_service import LLMService
from core.indexing_pipeline import IndexingPipeline


class RAGService:
    """Service principal pour coordonner les fonctionnalités RAG."""
    
    def __init__(self):
        self.es_manager = ElasticsearchManager()
        self.llm_service = LLMService()
        self.indexing_pipeline = IndexingPipeline()
        
        # Configurer la chaîne RAG
        retriever = self.es_manager.get_retriever(k=5)
        self.llm_service.setup_rag_chain(retriever)
    
    def process_query(self, query: str, use_rag: bool = True) -> Dict[str, Any]:
        """Traiter une requête utilisateur avec le système RAG."""
        if not query:
            return {"answer": "Veuillez poser une question.", "context": [], "sources": []}
        
        if use_rag:
            # Récupérer les documents pertinents
            search_results = self.es_manager.search_documents(query, k=5)
            
            if not search_results:
                return {
                    "answer": "Je n'ai pas trouvé d'informations pertinentes pour répondre à votre question. "
                             "Essayez de reformuler votre question ou d'ajouter plus de documents à la base de connaissances.",
                    "context": [],
                    "sources": []
                }
            
            # Générer une réponse basée sur les documents
            response = self.llm_service.generate_response(query, context=search_results)
            
            # Extraire les sources des documents
            sources = []
            for result in search_results:
                if "metadata" in result and "source" in result["metadata"]:
                    source = result["metadata"]["source"]
                    if source not in sources:
                        sources.append(source)
            
            return {
                "answer": response,
                "context": [item["text"] for item in search_results],
                "sources": sources
            }
        else:
            # Réponse directe sans RAG
            response = self.llm_service.generate_response(query, context=[])
            
            return {
                "answer": response,
                "context": [],
                "sources": []
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir des statistiques sur l'état actuel du système."""
        doc_count = self.es_manager.get_document_count()
        
        return {
            "document_count": doc_count,
            "index_name": self.es_manager.index_name,
            "llm_provider": self.llm_service.provider
        }
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Répondre dans un contexte de chat."""
        if not messages:
            return "Veuillez fournir des messages pour le chat."
        
        return self.llm_service.chat(messages) 