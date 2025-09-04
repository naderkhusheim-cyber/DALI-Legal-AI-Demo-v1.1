"""
DALI Legal AI - Main Streamlit Web Application
User-friendly interface for legal professionals
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.llm_engine import LLMEngine
from core.vector_store import VectorStore, create_legal_document_metadata
from scrapers.firecrawl_scraper import FirecrawlScraper
from utils.document_processor import DocumentProcessor
from utils.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        background: linear-gradient(135deg, #1f4e79 0%, #2c5f2d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #c5a572;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1f4e79 0%, #2c5f2d 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


class DALIApp:
    """Main DALI Legal AI Application"""
    
    def __init__(self):
        self.config = load_config()
        self.initialize_components()
        self.initialize_session_state()
    
    def initialize_components(self):
        """Initialize AI components"""
        try:
            # Initialize LLM Engine
            self.llm_engine = LLMEngine(
                model_name=self.config.get('ollama', {}).get('model', 'llama3'),
                host=self.config.get('ollama', {}).get('host', 'localhost'),
                port=self.config.get('ollama', {}).get('port', 11434)
            )
            
            # Initialize Vector Store
            self.vector_store = VectorStore(
                persist_directory=self.config.get('chroma', {}).get('persist_directory', './data/embeddings'),
                collection_name=self.config.get('chroma', {}).get('collection_name', 'legal_documents')
            )
            
            # Initialize Web Scraper
            self.scraper = FirecrawlScraper(
                api_key=self.config.get('firecrawl', {}).get('api_key')
            )
            
            # Initialize Document Processor
            self.doc_processor = DocumentProcessor()
            
            st.session_state.components_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            st.session_state.components_initialized = False
            st.session_state.initialization_error = str(e)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        
        if 'uploaded_documents' not in st.session_state:
            st.session_state.uploaded_documents = []
        
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
    
    def render_sidebar(self):
        """Render the sidebar with navigation and system status"""
        with st.sidebar:
            # Logo and branding
            st.markdown("""
            <div class="sidebar-logo">
                <h2>⚖️ DALI</h2>
                <p>Development of Ambitious Leading Ideas</p>
                <small>دائرة أفكار رائدة مبتكرة</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            st.markdown("### Navigation")
            page = st.selectbox(
                "Select Page",
                ["🏠 Dashboard", "🔍 Legal Research", "📄 Document Analysis", 
                 "📚 Knowledge Base", "🌐 Web Research", "⚙️ Settings"],
                key="navigation"
            )
            
            # System Status
            st.markdown("### System Status")
            
            if hasattr(st.session_state, 'components_initialized'):
                if st.session_state.components_initialized:
                    # Check component health
                    llm_status = self.llm_engine.health_check() if hasattr(self, 'llm_engine') else False
                    scraper_status = self.scraper.health_check() if hasattr(self, 'scraper') else False
                    
                    st.success("✅ System Initialized") if llm_status else st.error("❌ LLM Engine Error")
                    st.success("✅ Vector Store Ready") if hasattr(self, 'vector_store') else st.error("❌ Vector Store Error")
                    st.success("✅ Web Scraper Ready") if scraper_status else st.warning("⚠️ Web Scraper Limited")
                else:
                    st.error("❌ Initialization Failed")
                    if hasattr(st.session_state, 'initialization_error'):
                        st.error(st.session_state.initialization_error)
            
            # Quick Stats
            if hasattr(self, 'vector_store'):
                try:
                    stats = self.vector_store.get_collection_stats()
                    st.markdown("### Quick Stats")
                    st.metric("Documents", stats.get('total_documents', 0))
                    st.metric("Conversations", len(st.session_state.conversation_history))
                except Exception as e:
                    logger.error(f"Error getting stats: {e}")
            
            return page
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.markdown("""
        <div class="main-header">
            <h1>⚖️ DALI Legal AI System</h1>
            <p>Your intelligent legal research and document analysis assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome message
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🔍 Legal Research</h3>
                <p>Conduct comprehensive legal research with AI-powered insights and citations.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📄 Document Analysis</h3>
                <p>Analyze contracts, agreements, and legal documents with advanced AI.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 Knowledge Management</h3>
                <p>Build and search your firm's legal knowledge base with semantic search.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent Activity
        st.markdown("### Recent Activity")
        
        if st.session_state.conversation_history:
            recent_conversations = st.session_state.conversation_history[-5:]
            for i, conv in enumerate(reversed(recent_conversations)):
                with st.expander(f"Conversation {len(st.session_state.conversation_history) - i}"):
                    st.write(f"**Query:** {conv.get('query', 'N/A')[:100]}...")
                    st.write(f"**Time:** {conv.get('timestamp', 'N/A')}")
        else:
            st.info("No recent activity. Start by asking a legal question or uploading a document.")
        
        # Quick Actions
        st.markdown("### Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Start Legal Research", use_container_width=True):
                st.session_state.navigation = "🔍 Legal Research"
                st.rerun()
        
        with col2:
            if st.button("📄 Analyze Document", use_container_width=True):
                st.session_state.navigation = "📄 Document Analysis"
                st.rerun()
        
        with col3:
            if st.button("🌐 Web Research", use_container_width=True):
                st.session_state.navigation = "🌐 Web Research"
                st.rerun()
    
    def render_legal_research(self):
        """Render the legal research interface"""
        st.header("🔍 Legal Research")
        st.markdown("Ask legal questions and get AI-powered research with citations and analysis.")
        
        # Research query input
        query = st.text_area(
            "Enter your legal research question:",
            placeholder="e.g., What are the requirements for forming a limited liability company in Saudi Arabia?",
            height=100
        )
        
        # Research options
        col1, col2 = st.columns(2)
        with col1:
            jurisdiction = st.selectbox(
                "Jurisdiction",
                ["Saudi Arabia", "GCC Countries", "International", "Other"],
                index=0
            )
        
        with col2:
            include_web_search = st.checkbox("Include web research", value=True)
        
        # Research button
        if st.button("🔍 Conduct Research", type="primary", use_container_width=True):
            if query.strip():
                with st.spinner("Conducting legal research..."):
                    try:
                        # Perform research
                        research_result = self.llm_engine.legal_research(query, jurisdiction)
                        
                        # Search knowledge base
                        kb_results = self.vector_store.search(query, n_results=3)
                        
                        # Web research if enabled
                        web_results = []
                        if include_web_search and hasattr(self, 'scraper'):
                            web_results = self.scraper.search_legal_databases(query)
                        
                        # Display results
                        st.markdown("### Research Results")
                        
                        # AI Analysis
                        st.markdown("#### AI Legal Analysis")
                        st.markdown(research_result)
                        
                        # Knowledge Base Results
                        if kb_results:
                            st.markdown("#### Related Documents from Knowledge Base")
                            for i, result in enumerate(kb_results):
                                with st.expander(f"Document {i+1}: {result['metadata'].get('title', 'Unknown')}"):
                                    st.write(result['content'][:500] + "...")
                                    st.write(f"**Relevance Score:** {result['score']:.2f}")
                        
                        # Web Research Results
                        if web_results:
                            st.markdown("#### Web Research Results")
                            for i, result in enumerate(web_results):
                                if result.success:
                                    with st.expander(f"Source {i+1}: {result.title}"):
                                        st.write(f"**URL:** {result.url}")
                                        st.write(result.content[:500] + "...")
                        
                        # Save to conversation history
                        st.session_state.conversation_history.append({
                            'query': query,
                            'response': research_result,
                            'timestamp': datetime.now().isoformat(),
                            'type': 'legal_research',
                            'jurisdiction': jurisdiction
                        })
                        
                        st.success("Research completed successfully!")
                        
                    except Exception as e:
                        st.error(f"Error conducting research: {str(e)}")
            else:
                st.warning("Please enter a research question.")
    
    def render_document_analysis(self):
        """Render the document analysis interface"""
        st.header("📄 Document Analysis")
        st.markdown("Upload and analyze legal documents with AI-powered insights.")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload legal documents",
            type=['pdf', 'docx', 'txt', 'md'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.markdown(f"### Analysis: {uploaded_file.name}")
                
                # Analysis options
                col1, col2 = st.columns(2)
                with col1:
                    analysis_type = st.selectbox(
                        "Analysis Type",
                        ["general", "contract", "litigation", "compliance"],
                        key=f"analysis_type_{uploaded_file.name}"
                    )
                
                with col2:
                    add_to_kb = st.checkbox(
                        "Add to Knowledge Base",
                        key=f"add_kb_{uploaded_file.name}"
                    )
                
                if st.button(f"Analyze {uploaded_file.name}", key=f"analyze_{uploaded_file.name}"):
                    with st.spinner(f"Analyzing {uploaded_file.name}..."):
                        try:
                            # Process document
                            document_text = self.doc_processor.process_file(uploaded_file)
                            
                            if document_text:
                                # Perform analysis
                                analysis_result = self.llm_engine.analyze_document(
                                    document_text, analysis_type
                                )
                                
                                # Display results
                                st.markdown("#### Analysis Results")
                                st.markdown(analysis_result)
                                
                                # Add to knowledge base if requested
                                if add_to_kb:
                                    metadata = create_legal_document_metadata(
                                        title=uploaded_file.name,
                                        document_type=analysis_type,
                                        source="uploaded_document",
                                        date_created=datetime.now().isoformat()
                                    )
                                    
                                    doc_ids = self.vector_store.add_document(
                                        document_text, metadata
                                    )
                                    
                                    st.success(f"Document added to knowledge base with {len(doc_ids)} chunks")
                                
                                # Save analysis
                                st.session_state.conversation_history.append({
                                    'query': f"Document analysis: {uploaded_file.name}",
                                    'response': analysis_result,
                                    'timestamp': datetime.now().isoformat(),
                                    'type': 'document_analysis',
                                    'analysis_type': analysis_type
                                })
                                
                            else:
                                st.error("Could not extract text from document")
                                
                        except Exception as e:
                            st.error(f"Error analyzing document: {str(e)}")
    
    def render_knowledge_base(self):
        """Render the knowledge base interface"""
        st.header("📚 Knowledge Base")
        st.markdown("Search and manage your firm's legal knowledge base.")
        
        # Search interface
        search_query = st.text_input(
            "Search knowledge base:",
            placeholder="Enter search terms or legal concepts..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            num_results = st.slider("Number of results", 1, 20, 5)
        
        with col2:
            min_score = st.slider("Minimum relevance score", 0.0, 1.0, 0.5)
        
        if st.button("🔍 Search Knowledge Base", type="primary"):
            if search_query.strip():
                with st.spinner("Searching knowledge base..."):
                    try:
                        results = self.vector_store.similarity_search_with_score_threshold(
                            search_query, score_threshold=min_score, max_results=num_results
                        )
                        
                        if results:
                            st.markdown(f"### Found {len(results)} relevant documents")
                            
                            for i, result in enumerate(results):
                                with st.expander(
                                    f"Result {i+1}: {result['metadata'].get('title', 'Unknown')} "
                                    f"(Score: {result['score']:.2f})"
                                ):
                                    st.markdown("**Content:**")
                                    st.write(result['content'])
                                    
                                    st.markdown("**Metadata:**")
                                    metadata_df = pd.DataFrame([result['metadata']])
                                    st.dataframe(metadata_df)
                        else:
                            st.info("No documents found matching your search criteria.")
                            
                    except Exception as e:
                        st.error(f"Error searching knowledge base: {str(e)}")
            else:
                st.warning("Please enter a search query.")
        
        # Knowledge base statistics
        st.markdown("### Knowledge Base Statistics")
        try:
            stats = self.vector_store.get_collection_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Documents", stats.get('total_documents', 0))
            with col2:
                st.metric("Document Types", len(stats.get('document_types', {})))
            with col3:
                st.metric("Sources", len(stats.get('sources', {})))
            
            # Document types breakdown
            if stats.get('document_types'):
                st.markdown("#### Document Types")
                doc_types_df = pd.DataFrame(
                    list(stats['document_types'].items()),
                    columns=['Document Type', 'Count']
                )
                st.bar_chart(doc_types_df.set_index('Document Type'))
                
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
    
    def render_web_research(self):
        """Render the web research interface"""
        st.header("🌐 Web Research")
        st.markdown("Conduct web research on legal topics using AI-powered scraping.")
        
        # URL input
        research_urls = st.text_area(
            "Enter URLs to research (one per line):",
            placeholder="https://laws.boe.gov.sa\nhttps://www.moj.gov.sa",
            height=100
        )
        
        # Research options
        col1, col2 = st.columns(2)
        with col1:
            max_pages = st.number_input("Max pages per site", 1, 50, 5)
        
        with col2:
            add_to_kb = st.checkbox("Add results to knowledge base", value=True)
        
        if st.button("🌐 Start Web Research", type="primary"):
            if research_urls.strip():
                urls = [url.strip() for url in research_urls.split('\n') if url.strip()]
                
                with st.spinner(f"Researching {len(urls)} websites..."):
                    try:
                        all_results = []
                        
                        for url in urls:
                            st.write(f"Researching: {url}")
                            
                            # Scrape the URL
                            result = self.scraper.scrape_url(url)
                            
                            if result.success:
                                all_results.append(result)
                                
                                # Display result
                                with st.expander(f"Results from {url}"):
                                    st.write(f"**Title:** {result.title}")
                                    st.write(f"**Content Preview:** {result.content[:500]}...")
                                    
                                    # Extract legal citations
                                    citations = self.scraper.extract_legal_citations(result.content)
                                    if citations:
                                        st.write("**Legal Citations Found:**")
                                        for citation in citations[:5]:  # Show first 5
                                            st.write(f"- {citation['type']}: {citation['reference']}")
                                
                                # Add to knowledge base if requested
                                if add_to_kb:
                                    metadata = create_legal_document_metadata(
                                        title=result.title,
                                        document_type="web_research",
                                        source=url,
                                        date_created=datetime.now().isoformat()
                                    )
                                    
                                    self.vector_store.add_document(result.content, metadata)
                            else:
                                st.error(f"Failed to scrape {url}: {result.error}")
                        
                        if all_results:
                            st.success(f"Successfully researched {len(all_results)} websites!")
                            
                            # Save to session state
                            st.session_state.conversation_history.append({
                                'query': f"Web research: {len(urls)} URLs",
                                'response': f"Researched {len(all_results)} websites successfully",
                                'timestamp': datetime.now().isoformat(),
                                'type': 'web_research',
                                'urls': urls
                            })
                        
                    except Exception as e:
                        st.error(f"Error during web research: {str(e)}")
            else:
                st.warning("Please enter at least one URL to research.")
    
    def render_settings(self):
        """Render the settings interface"""
        st.header("⚙️ Settings")
        st.markdown("Configure DALI Legal AI system settings.")
        
        # System Configuration
        st.markdown("### System Configuration")
        
        # LLM Settings
        with st.expander("🧠 LLM Engine Settings"):
            current_model = st.selectbox(
                "Current Model",
                ["llama3", "mistral", "codellama"],
                index=0
            )
            
            temperature = st.slider("Response Temperature", 0.0, 1.0, 0.3)
            max_tokens = st.number_input("Max Response Tokens", 100, 4000, 2048)
            
            if st.button("Update LLM Settings"):
                st.success("LLM settings updated!")
        
        # Vector Store Settings
        with st.expander("📚 Vector Store Settings"):
            chunk_size = st.number_input("Document Chunk Size", 500, 2000, 1000)
            chunk_overlap = st.number_input("Chunk Overlap", 50, 500, 200)
            
            if st.button("Update Vector Store Settings"):
                st.success("Vector store settings updated!")
        
        # Data Management
        st.markdown("### Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Conversation History", type="secondary"):
                st.session_state.conversation_history = []
                st.success("Conversation history cleared!")
        
        with col2:
            if st.button("🗑️ Reset Knowledge Base", type="secondary"):
                if st.checkbox("I understand this will delete all documents"):
                    try:
                        self.vector_store.reset_collection()
                        st.success("Knowledge base reset successfully!")
                    except Exception as e:
                        st.error(f"Error resetting knowledge base: {str(e)}")
        
        # Export/Import
        st.markdown("### Export/Import")
        
        if st.button("📥 Export Conversation History"):
            if st.session_state.conversation_history:
                export_data = json.dumps(st.session_state.conversation_history, indent=2)
                st.download_button(
                    "Download History",
                    export_data,
                    file_name=f"dali_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.info("No conversation history to export.")
    
    def run(self):
        """Run the main application"""
        try:
            # Render sidebar and get selected page
            selected_page = self.render_sidebar()
            
            # Check if components are initialized
            if not hasattr(st.session_state, 'components_initialized') or not st.session_state.components_initialized:
                st.error("System initialization failed. Please check the configuration and try again.")
                return
            
            # Route to appropriate page
            if selected_page == "🏠 Dashboard":
                self.render_dashboard()
            elif selected_page == "🔍 Legal Research":
                self.render_legal_research()
            elif selected_page == "📄 Document Analysis":
                self.render_document_analysis()
            elif selected_page == "📚 Knowledge Base":
                self.render_knowledge_base()
            elif selected_page == "🌐 Web Research":
                self.render_web_research()
            elif selected_page == "⚙️ Settings":
                self.render_settings()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    # Initialize and run the application
    app = DALIApp()
    app.run()

