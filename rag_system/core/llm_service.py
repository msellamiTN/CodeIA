from typing import List, Dict, Any, Optional, Union

import google.generativeai as genai
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from config.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_URL,
    OLLAMA_MODEL
)


class LLMService:
    """Service pour interagir avec différents modèles LLM."""
    
    def __init__(self):
        self.provider = LLM_PROVIDER.lower()
        
        if self.provider == "gemini":
            # Configurer l'API Gemini
            if not GEMINI_API_KEY:
                raise ValueError("Clé API Gemini non configurée. Veuillez l'ajouter dans le fichier .env")
            
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.llm_chain = None
        
        elif self.provider == "ollama":
            # Configurer Ollama
            self.ollama = Ollama(base_url=OLLAMA_URL, model=OLLAMA_MODEL)
            self.llm_chain = None
        
        else:
            raise ValueError(f"Fournisseur LLM non pris en charge: {self.provider}")
    
    def _get_rag_prompt_template(self) -> str:
        """Obtenir le template de prompt pour les requêtes RAG."""
        return """
        Vous êtes un assistant IA utile qui fournit des informations précises et pertinentes.
        
        Utilisez le contexte suivant pour répondre à la question de l'utilisateur.
        Si vous ne trouvez pas la réponse dans le contexte, dites-le honnêtement au lieu de deviner.
        
        CONTEXTE:
        {context}
        
        QUESTION: {question}
        
        RÉPONSE:
        """
    
    def setup_rag_chain(self, retriever):
        """Configurer la chaîne RAG avec le retriever fourni."""
        rag_prompt = PromptTemplate.from_template(self._get_rag_prompt_template())
        
        if self.provider == "gemini":
            # On utilisera directement l'API pour Gemini
            self.llm_chain = None
            self.retriever = retriever
        
        elif self.provider == "ollama":
            # Configurer la chaîne LangChain pour Ollama
            self.llm_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | rag_prompt
                | self.ollama
                | StrOutputParser()
            )
    
    def generate_response(self, query: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """Générer une réponse en utilisant le modèle LLM configuré."""
        if not context:
            if hasattr(self, 'retriever') and self.retriever:
                context_docs = self.retriever.get_relevant_documents(query)
                context = [{"text": doc.page_content, "source": doc.metadata.get("source", "inconnu")} 
                          for doc in context_docs]
            else:
                context = []
        
        if self.provider == "gemini":
            # Formater le contexte et la requête pour Gemini
            prompt = self._get_rag_prompt_template().format(
                context="\n\n".join([item["text"] for item in context]),
                question=query
            )
            
            response = self.model.generate_content(prompt)
            return response.text
        
        elif self.provider == "ollama":
            if self.llm_chain:
                return self.llm_chain.invoke(query)
            else:
                # Fallback si la chaîne n'est pas configurée
                prompt = self._get_rag_prompt_template().format(
                    context="\n\n".join([item["text"] for item in context]),
                    question=query
                )
                return self.ollama.invoke(prompt)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Effectuer une conversation en mode chat."""
        if self.provider == "gemini":
            # Convertir les messages au format attendu par Gemini
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            
            response = self.model.generate_content(gemini_messages)
            return response.text
        
        elif self.provider == "ollama":
            # Convertir les messages au format LangChain
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            response = self.ollama.invoke(langchain_messages)
            return response 