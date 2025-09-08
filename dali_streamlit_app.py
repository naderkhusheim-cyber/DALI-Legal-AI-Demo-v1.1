#!/usr/bin/env python3
"""
DALI Legal AI MVP - Streamlit Web Interface
Development of Ambitious Leading Ideas @ Siyada Tech

A user-friendly web interface for the DALI Legal AI system
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from dali_technical_implementation import DALILegalAI

# Page configuration
st.set_page_config(
    page_title="DALI Legal AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'dali_system' not in st.session_state:
        st.session_state.dali_system = DALILegalAI()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_added' not in st.session_state:
        st.session_state.documents_added = 0

def display_system_status():
    """Display system status in sidebar"""
    st.sidebar.markdown("## 🔧 System Status")
    
    dali = st.session_state.dali_system
    
    # Check Ollama status
    ollama_status = dali.check_ollama_status()
    if ollama_status:
        st.sidebar.markdown('<div class="status-box status-success">✅ Ollama: Running</div>', unsafe_allow_html=True)
        models = dali.list_available_models()
        if models:
            st.sidebar.selectbox("Select Model", models, key="selected_model")
        else:
            st.sidebar.warning("No models available. Run: ollama pull llama3")
    else:
        st.sidebar.markdown('<div class="status-box status-error">❌ Ollama: Not Running</div>', unsafe_allow_html=True)
        st.sidebar.error("Please start Ollama: `ollama serve`")
    
    # Check Firecrawl API
    if dali.firecrawl_api_key:
        st.sidebar.markdown('<div class="status-box status-success">✅ Firecrawl: Configured</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-box status-warning">⚠️ Firecrawl: Not Configured</div>', unsafe_allow_html=True)
        st.sidebar.info("Set FIRECRAWL_API_KEY environment variable")
    
    # Vector database status
    try:
        collection_count = st.session_state.dali_system.collection.count()
        st.sidebar.markdown('<div class="status-box status-success">✅ Vector DB: Ready</div>', unsafe_allow_html=True)
        st.sidebar.info(f"Documents in database: {collection_count}")
    except:
        st.sidebar.markdown('<div class="status-box status-error">❌ Vector DB: Error</div>', unsafe_allow_html=True)

def main_interface():
    """Main application interface"""
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ DALI Legal AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Development of Ambitious Leading Ideas @ Siyada Tech</p>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🌐 Web Scraping", "📚 Document Management", "📊 Analytics"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        web_scraping_interface()
    
    with tab3:
        document_management_interface()
    
    with tab4:
        analytics_interface()

def chat_interface():
    """Legal AI chat interface"""
    st.markdown("## 💬 Legal AI Assistant")
    st.markdown("Ask questions about your legal documents using natural language.")
    
    # Chat input
    user_question = st.text_input(
        "Ask a legal question:",
        placeholder="e.g., What are the key elements of a valid contract?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("Ask Question", type="primary")
    with col2:
        clear_chat = st.button("Clear Chat History")
    
    if clear_chat:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask_button and user_question:
        with st.spinner("Searching legal documents and generating response..."):
            # Get selected model
            selected_model = st.session_state.get("selected_model", "llama3")
            
            # Perform RAG query
            result = st.session_state.dali_system.legal_rag_query(user_question, selected_model)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "timestamp": datetime.now(),
                "question": user_question,
                "answer": result["answer"],
                "sources": result["sources"],
                "context_used": result["context_used"]
            })
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"Q: {chat['question']}", expanded=(i==0)):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                st.markdown(f"**Sources Used:** {chat['context_used']} documents")
                if chat['sources']:
                    st.markdown("**Source Details:**")
                    for source in chat['sources']:
                        st.json(source)
                st.markdown(f"*Asked at: {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}*")

def web_scraping_interface():
    """Web scraping interface"""
    st.markdown("## 🌐 Legal Web Scraping")
    st.markdown("Scrape legal websites and add content to your knowledge base.")
    
    # URL input
    url_to_scrape = st.text_input(
        "Enter URL to scrape:",
        placeholder="https://example-legal-site.com/article",
        key="scrape_url"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        scrape_button = st.button("Scrape Website", type="primary")
    with col2:
        add_to_db = st.checkbox("Add to knowledge base", value=True)
    
    if scrape_button and url_to_scrape:
        if not st.session_state.dali_system.firecrawl_api_key:
            st.error("Firecrawl API key not configured. Please set FIRECRAWL_API_KEY environment variable.")
            return
        
        with st.spinner("Scraping website..."):
            result = st.session_state.dali_system.scrape_with_firecrawl(url_to_scrape)
            
            if "error" in result:
                st.error(f"Scraping failed: {result['error']}")
            else:
                st.success("Website scraped successfully!")
                
                # Display scraped content
                if "data" in result and "markdown" in result["data"]:
                    content = result["data"]["markdown"]
                    st.markdown("### 📄 Scraped Content Preview")
                    st.text_area("Content", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                    
                    if add_to_db:
                        # Add to vector database
                        metadata = {
                            "source": url_to_scrape,
                            "type": "web_scraped",
                            "scraped_at": datetime.now().isoformat(),
                            "title": result["data"].get("title", "Unknown")
                        }
                        
                        if st.session_state.dali_system.add_document_to_vectordb(content, metadata):
                            st.success("Content added to knowledge base!")
                            st.session_state.documents_added += 1
                        else:
                            st.error("Failed to add content to knowledge base.")

def document_management_interface():
    """Document management interface"""
    st.markdown("## 📚 Document Management")
    st.markdown("Upload and manage legal documents in your knowledge base.")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload legal documents",
        type=['txt', 'md', 'pdf'],
        accept_multiple_files=True,
        key="doc_upload"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"### 📄 {uploaded_file.name}")
            
            # Read file content
            if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.md'):
                content = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.name.endswith('.pdf'):
                st.warning("PDF processing not implemented in MVP. Please convert to text first.")
                continue
            else:
                st.error(f"Unsupported file type: {uploaded_file.type}")
                continue
            
            # Display content preview
            st.text_area(f"Content preview - {uploaded_file.name}", content[:500] + "..." if len(content) > 500 else content, height=150)
            
            # Add to database button
            if st.button(f"Add {uploaded_file.name} to Knowledge Base", key=f"add_{uploaded_file.name}"):
                metadata = {
                    "source": uploaded_file.name,
                    "type": "uploaded_document",
                    "uploaded_at": datetime.now().isoformat(),
                    "file_size": len(content)
                }
                
                if st.session_state.dali_system.add_document_to_vectordb(content, metadata):
                    st.success(f"✅ {uploaded_file.name} added to knowledge base!")
                    st.session_state.documents_added += 1
                else:
                    st.error(f"❌ Failed to add {uploaded_file.name} to knowledge base.")
    
    # Document search
    st.markdown("### 🔍 Search Documents")
    search_query = st.text_input("Search in knowledge base:", key="doc_search")
    
    if search_query:
        with st.spinner("Searching documents..."):
            results = st.session_state.dali_system.search_documents(search_query, n_results=10)
            
            if results:
                st.markdown(f"Found {len(results)} relevant documents:")
                for i, doc in enumerate(results):
                    with st.expander(f"Document {i+1} (Similarity: {1-doc['distance']:.3f})"):
                        st.markdown(f"**Content:** {doc['content'][:300]}...")
                        st.json(doc['metadata'])
            else:
                st.info("No documents found matching your search.")

def analytics_interface():
    """Analytics and system information"""
    st.markdown("## 📊 System Analytics")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Documents Added", st.session_state.documents_added)
    
    with col2:
        try:
            total_docs = st.session_state.dali_system.collection.count()
            st.metric("Total Documents", total_docs)
        except:
            st.metric("Total Documents", "Error")
    
    with col3:
        st.metric("Chat Sessions", len(st.session_state.chat_history))
    
    with col4:
        models = st.session_state.dali_system.list_available_models()
        st.metric("Available Models", len(models))
    
    # Model information
    st.markdown("### 🤖 Available Models")
    models = st.session_state.dali_system.list_available_models()
    if models:
        model_df = pd.DataFrame({"Model Name": models})
        st.dataframe(model_df, use_container_width=True)
    else:
        st.info("No models available. Install models using: `ollama pull <model_name>`")
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    if st.session_state.chat_history:
        recent_chats = st.session_state.chat_history[-5:]  # Last 5 chats
        activity_data = []
        for chat in recent_chats:
            activity_data.append({
                "Timestamp": chat["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "Question": chat["question"][:50] + "..." if len(chat["question"]) > 50 else chat["question"],
                "Sources Used": chat["context_used"]
            })
        
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No recent activity.")

def main():
    """Main application entry point"""
    initialize_session_state()
    display_system_status()
    main_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🚀 **DALI Legal AI MVP** - Development of Ambitious Leading Ideas @ Siyada Tech | "
        "Built with ❤️ using Ollama, Firecrawl, and Chroma"
    )

if __name__ == "__main__":
    main()

