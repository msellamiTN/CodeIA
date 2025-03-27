import os
import sys
import time
from pathlib import Path

import streamlit as st

# Ajouter le répertoire parent au chemin de recherche Python
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from core.rag_service import RAGService
from core.indexing_pipeline import IndexingPipeline
from config.config import APP_NAME, APP_DESCRIPTION


# Configuration de la page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser les services dans une fonction pour éviter la réinitialisation à chaque interaction
@st.cache_resource
def init_services():
    return {
        "rag_service": RAGService(),
        "indexing_pipeline": IndexingPipeline()
    }

# Récupérer les services
services = init_services()
rag_service = services["rag_service"]
indexing_pipeline = services["indexing_pipeline"]

# Initialiser l'historique des messages s'il n'existe pas dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialiser le mode d'utilisation
if "use_rag" not in st.session_state:
    st.session_state.use_rag = True


def main():
    # Titre et description
    st.title(APP_NAME)
    st.markdown(APP_DESCRIPTION)
    
    # Créer deux colonnes principales
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Section téléchargement de documents
        st.header("📄 Télécharger des Documents")
        
        # Afficher les statistiques
        stats = rag_service.get_stats()
        st.info(f"Documents indexés: {stats['document_count']}\nModèle LLM: {stats['llm_provider']}")
        
        # Option pour télécharger un fichier
        uploaded_file = st.file_uploader(
            "Choisissez un fichier (PDF, TXT, JSON)",
            type=["pdf", "txt", "json"]
        )
        
        if uploaded_file:
            with st.spinner("Traitement du fichier en cours..."):
                file_path = indexing_pipeline.save_uploaded_file(uploaded_file)
                if file_path:
                    st.success(f"Le fichier {uploaded_file.name} a été traité avec succès!")
                else:
                    st.error(f"Erreur lors du traitement du fichier {uploaded_file.name}")
        
        # Option pour réindexer tous les documents
        if st.button("Réindexer tous les documents"):
            with st.spinner("Réindexation en cours..."):
                indexing_pipeline.clear_index()
                num_indexed = indexing_pipeline.index_directory()
                st.success(f"Réindexation terminée. {num_indexed} chunks indexés.")
        
        # Option pour choisir entre RAG et requête directe
        st.header("⚙️ Options")
        st.session_state.use_rag = st.checkbox("Utiliser la récupération augmentée (RAG)", value=st.session_state.use_rag)
    
    with col1:
        # Section Questions & Réponses
        st.header("🤖 Questions & Réponses")
        
        # Afficher l'historique des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    st.caption(f"Sources: {', '.join(message['sources'])}")
        
        # Zone de saisie de la question
        query = st.chat_input("Posez votre question ici...")
        
        # Traiter la question de l'utilisateur
        if query:
            # Ajouter la question à l'historique
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Afficher la question
            with st.chat_message("user"):
                st.markdown(query)
            
            # Générer la réponse
            with st.chat_message("assistant"):
                with st.spinner("Réflexion en cours..."):
                    response = rag_service.process_query(query, use_rag=st.session_state.use_rag)
                    
                    # Afficher la réponse
                    st.markdown(response["answer"])
                    
                    # Afficher les sources si disponibles
                    if response["sources"]:
                        st.caption(f"Sources: {', '.join(response['sources'])}")
            
            # Ajouter la réponse à l'historique
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            })
            
            # Afficher le contexte récupéré si RAG est activé
            if st.session_state.use_rag and response["context"]:
                with st.expander("Voir le contexte récupéré"):
                    for i, ctx in enumerate(response["context"], 1):
                        st.markdown(f"**Extrait {i}:**\n{ctx}")


if __name__ == "__main__":
    main() 