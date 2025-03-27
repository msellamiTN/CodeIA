import time
from typing import List, Dict, Any, Optional

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError
from langchain_elasticsearch import ElasticsearchStore
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

from config.config import (
    ELASTICSEARCH_URL,
    ELASTICSEARCH_INDEX,
    EMBEDDING_MODEL
)


class ElasticsearchManager:
    """Classe pour gérer les interactions avec ElasticSearch."""
    
    def __init__(self):
        self.es_url = ELASTICSEARCH_URL
        self.index_name = ELASTICSEARCH_INDEX
        self.client = Elasticsearch(self.es_url)
        
        # Initialiser le modèle d'embedding
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Attendre que ElasticSearch soit disponible
        self._wait_for_elasticsearch()
        
        # Créer l'index s'il n'existe pas
        self._create_index_if_not_exists()
    
    def _wait_for_elasticsearch(self, max_retries: int = 10, retry_interval: int = 5):
        """Attendre que ElasticSearch soit disponible."""
        retries = 0
        while retries < max_retries:
            try:
                if self.client.ping():
                    print("Connexion à ElasticSearch établie.")
                    return True
            except Exception as e:
                retries += 1
                print(f"Tentative de connexion à ElasticSearch ({retries}/{max_retries}): {str(e)}")
                time.sleep(retry_interval)
        
        raise ConnectionError("Impossible de se connecter à ElasticSearch après plusieurs tentatives.")
    
    def _create_index_if_not_exists(self):
        """Créer l'index ElasticSearch s'il n'existe pas déjà."""
        if not self.client.indices.exists(index=self.index_name):
            try:
                # Définir le mapping pour stocker les embeddings
                mapping = {
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "metadata": {"type": "object"},
                            "vector": {
                                "type": "dense_vector",
                                "dims": 384,  # Dimension de all-MiniLM-L6-v2
                                "index": True,
                                "similarity": "cosine"
                            }
                        }
                    }
                }
                
                self.client.indices.create(index=self.index_name, body=mapping)
                print(f"Index '{self.index_name}' créé avec succès.")
            except RequestError as e:
                print(f"Erreur lors de la création de l'index: {str(e)}")
    
    def index_documents(self, documents: List[Document]) -> int:
        """Indexer les documents dans ElasticSearch."""
        if not documents:
            print("Aucun document à indexer.")
            return 0
        
        actions = []
        for i, doc in enumerate(documents):
            # Générer l'embedding du document
            embedding = self.embeddings.embed_query(doc.page_content)
            
            # Créer l'action d'indexation
            action = {
                "_index": self.index_name,
                "_source": {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "vector": embedding
                }
            }
            actions.append(action)
        
        # Indexer les documents par lots
        success, failed = helpers.bulk(self.client, actions, stats_only=True)
        print(f"Documents indexés: {success}, Échecs: {failed}")
        
        return success
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Rechercher des documents similaires à la requête."""
        # Générer l'embedding de la requête
        query_embedding = self.embeddings.embed_query(query)
        
        # Effectuer une recherche par similarité
        search_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            },
            "size": k
        }
        
        response = self.client.search(index=self.index_name, body=search_query)
        
        results = []
        for hit in response["hits"]["hits"]:
            results.append({
                "text": hit["_source"]["text"],
                "metadata": hit["_source"]["metadata"],
                "score": hit["_score"]
            })
        
        return results
    
    def get_retriever(self, k: int = 5):
        """Obtenir un retriever LangChain pour ElasticSearch."""
        return ElasticsearchStore(
            es_url=self.es_url,
            index_name=self.index_name,
            embedding=self.embeddings,
            query_field="text"
        ).as_retriever(search_kwargs={"k": k})
    
    def delete_all_documents(self):
        """Supprimer tous les documents de l'index."""
        try:
            self.client.delete_by_query(
                index=self.index_name,
                body={"query": {"match_all": {}}}
            )
            print(f"Tous les documents de l'index '{self.index_name}' ont été supprimés.")
        except Exception as e:
            print(f"Erreur lors de la suppression des documents: {str(e)}")
    
    def get_document_count(self) -> int:
        """Obtenir le nombre de documents dans l'index."""
        try:
            response = self.client.count(index=self.index_name)
            return response["count"]
        except Exception as e:
            print(f"Erreur lors du comptage des documents: {str(e)}")
            return 0 