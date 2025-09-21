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
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Default to English

# Translation system
LANGUAGES = {
    'en': {
        'system_status': 'System Status',
        'ollama_running': 'Ollama: Running',
        'ollama_not_running': 'Ollama: Not Running',
        'firecrawl_configured': 'Firecrawl: Configured',
        'firecrawl_not_configured': 'Firecrawl: Not Configured',
        'vector_db_ready': 'Vector DB: Ready',
        'vector_db_error': 'Vector DB: Error',
        'documents_in_db': 'Documents in database',
        'select_model': 'Select Model',
        'no_models_available': 'No models available. Run: ollama pull llama3',
        'start_ollama': 'Please start Ollama: `ollama serve`',
        'set_firecrawl_key': 'Set FIRECRAWL_API_KEY environment variable',
        'language_toggle': 'العربية',
        'chat': 'Chat',
        'web_scraping': 'Web Scraping',
        'document_management': 'Document Management',
        'analytics': 'Analytics',
        'legal_ai_assistant': 'Legal AI Assistant',
        'ask_questions': 'Ask questions about your legal documents using natural language.',
        'ask_legal_question': 'Ask a legal question:',
        'ask_question_placeholder': 'e.g., What are the key elements of a valid contract?',
        'ask_question_button': 'Ask Question',
        'clear_chat_history': 'Clear Chat History',
        'chat_history': 'Chat History',
        'question': 'Question',
        'answer': 'Answer',
        'sources_used': 'Sources Used',
        'source_details': 'Source Details',
        'asked_at': 'Asked at',
        'legal_web_scraping': 'Legal Web Scraping',
        'scrape_description': 'Scrape legal websites and add content to your knowledge base.',
        'enter_url': 'Enter URL to scrape:',
        'scrape_placeholder': 'https://example-legal-site.com/article',
        'scrape_button': 'Scrape Website',
        'add_to_kb': 'Add to knowledge base',
        'firecrawl_not_configured_error': 'Firecrawl API key not configured. Please set FIRECRAWL_API_KEY environment variable.',
        'scraping_website': 'Scraping website...',
        'scraping_failed': 'Scraping failed',
        'website_scraped_successfully': 'Website scraped successfully!',
        'scraped_content_preview': 'Scraped Content Preview',
        'content': 'Content',
        'content_added_to_kb': 'Content added to knowledge base!',
        'failed_to_add_content': 'Failed to add content to knowledge base.',
        'upload_manage_documents': 'Upload and manage legal documents in your knowledge base.',
        'upload_legal_documents': 'Upload legal documents',
        'file_limit': 'Max 200MB per file • PDF, DOCX, TXT, MD',
        'pdf_processing_not_implemented': 'PDF processing not implemented in MVP. Please convert to text first.',
        'unsupported_file_type': 'Unsupported file type',
        'content_preview': 'Content preview',
        'add_to_knowledge_base': 'Add to Knowledge Base',
        'added_to_kb': 'added to knowledge base!',
        'failed_to_add_to_kb': 'Failed to add to knowledge base.',
        'search_documents': 'Search Documents',
        'search_in_kb': 'Search in knowledge base:',
        'searching_documents': 'Searching documents...',
        'found_documents': 'Found relevant documents:',
        'document': 'Document',
        'similarity': 'Similarity',
        'no_documents_found': 'No documents found matching your search.',
        'system_analytics': 'System Analytics',
        'documents_added': 'Documents Added',
        'total_documents': 'Total Documents',
        'chat_sessions': 'Chat Sessions',
        'available_models': 'Available Models',
        'available_models_title': 'Available Models',
        'no_models_available_install': 'No models available. Install models using: `ollama pull <model_name>`',
        'recent_activity': 'Recent Activity',
        'no_recent_activity': 'No recent activity.',
        'timestamp': 'Timestamp',
        'sources_used_count': 'Sources Used',
        'footer_text': 'DALI Legal AI MVP - Development of Ambitious Leading Ideas @ Siyada Tech | Built with ❤️ using Ollama, Firecrawl, and Chroma'
    },
    'ar': {
        'system_status': 'حالة النظام',
        'ollama_running': 'أولاما: يعمل',
        'ollama_not_running': 'أولاما: لا يعمل',
        'firecrawl_configured': 'فايركرول: مُكوَّن',
        'firecrawl_not_configured': 'فايركرول: غير مُكوَّن',
        'vector_db_ready': 'قاعدة البيانات المتجهة: جاهزة',
        'vector_db_error': 'قاعدة البيانات المتجهة: خطأ',
        'documents_in_db': 'المستندات في قاعدة البيانات',
        'select_model': 'اختر النموذج',
        'no_models_available': 'لا توجد نماذج متاحة. تشغيل: ollama pull llama3',
        'start_ollama': 'يرجى تشغيل أولاما: `ollama serve`',
        'set_firecrawl_key': 'قم بتعيين متغير البيئة FIRECRAWL_API_KEY',
        'language_toggle': 'English',
        'chat': 'المحادثة',
        'web_scraping': 'استخراج الويب',
        'document_management': 'إدارة المستندات',
        'analytics': 'التحليلات',
        'legal_ai_assistant': 'مساعد الذكاء الاصطناعي القانوني',
        'ask_questions': 'اطرح أسئلة حول مستنداتك القانونية باستخدام اللغة الطبيعية.',
        'ask_legal_question': 'اطرح سؤالاً قانونياً:',
        'ask_question_placeholder': 'مثال: ما هي العناصر الأساسية للعقد الصحيح؟',
        'ask_question_button': 'اطرح السؤال',
        'clear_chat_history': 'مسح سجل المحادثة',
        'chat_history': 'سجل المحادثة',
        'question': 'السؤال',
        'answer': 'الإجابة',
        'sources_used': 'المصادر المستخدمة',
        'source_details': 'تفاصيل المصدر',
        'asked_at': 'طُلب في',
        'legal_web_scraping': 'استخراج الويب القانوني',
        'scrape_description': 'استخرج مواقع الويب القانونية وأضف المحتوى إلى قاعدة المعرفة الخاصة بك.',
        'enter_url': 'أدخل رابط الموقع للاستخراج:',
        'scrape_placeholder': 'https://example-legal-site.com/article',
        'scrape_button': 'استخراج الموقع',
        'add_to_kb': 'أضف إلى قاعدة المعرفة',
        'firecrawl_not_configured_error': 'مفتاح API لفايركرول غير مُكوَّن. يرجى تعيين متغير البيئة FIRECRAWL_API_KEY.',
        'scraping_website': 'جاري استخراج الموقع...',
        'scraping_failed': 'فشل الاستخراج',
        'website_scraped_successfully': 'تم استخراج الموقع بنجاح!',
        'scraped_content_preview': 'معاينة المحتوى المستخرج',
        'content': 'المحتوى',
        'content_added_to_kb': 'تم إضافة المحتوى إلى قاعدة المعرفة!',
        'failed_to_add_content': 'فشل في إضافة المحتوى إلى قاعدة المعرفة.',
        'upload_manage_documents': 'قم بتحميل وإدارة المستندات القانونية في قاعدة المعرفة الخاصة بك.',
        'upload_legal_documents': 'تحميل المستندات القانونية',
        'file_limit': 'الحد الأقصى 200 ميجابايت لكل ملف • PDF, DOCX, TXT, MD',
        'pdf_processing_not_implemented': 'معالجة PDF غير مُنفَّذة في MVP. يرجى التحويل إلى نص أولاً.',
        'unsupported_file_type': 'نوع الملف غير مدعوم',
        'content_preview': 'معاينة المحتوى',
        'add_to_knowledge_base': 'أضف إلى قاعدة المعرفة',
        'added_to_kb': 'تم إضافة إلى قاعدة المعرفة!',
        'failed_to_add_to_kb': 'فشل في إضافة إلى قاعدة المعرفة.',
        'search_documents': 'البحث في المستندات',
        'search_in_kb': 'البحث في قاعدة المعرفة:',
        'searching_documents': 'جاري البحث في المستندات...',
        'found_documents': 'تم العثور على مستندات ذات صلة:',
        'document': 'المستند',
        'similarity': 'التشابه',
        'no_documents_found': 'لم يتم العثور على مستندات تطابق بحثك.',
        'system_analytics': 'تحليلات النظام',
        'documents_added': 'المستندات المضافة',
        'total_documents': 'إجمالي المستندات',
        'chat_sessions': 'جلسات المحادثة',
        'available_models': 'النماذج المتاحة',
        'available_models_title': 'النماذج المتاحة',
        'no_models_available_install': 'لا توجد نماذج متاحة. قم بتثبيت النماذج باستخدام: `ollama pull <model_name>`',
        'recent_activity': 'النشاط الأخير',
        'no_recent_activity': 'لا يوجد نشاط حديث.',
        'timestamp': 'الوقت',
        'sources_used_count': 'المصادر المستخدمة',
        'footer_text': 'دالي للذكاء الاصطناعي القانوني MVP - تطوير الأفكار الطموحة الرائدة @ سيدة تك | مبني بـ ❤️ باستخدام أولاما وفايركرول وكروم'
    }
}

def t(key):
    """Translation function"""
    lang = st.session_state.language
    return LANGUAGES[lang].get(key, key)

def display_system_status():
    """Display system status in sidebar"""
    # Language toggle at the top
    st.sidebar.markdown("## 🌐 Language / اللغة")
    lang_toggle_label = t('language_toggle')
    if st.sidebar.button(lang_toggle_label, key='lang_toggle', help='Switch language / تبديل اللغة'):
        st.session_state.language = 'ar' if st.session_state.language == 'en' else 'en'
        st.rerun()
    
    st.sidebar.markdown("## 🔧 " + t('system_status'))
    
    dali = st.session_state.dali_system
    
    # Check Ollama status
    ollama_status = dali.check_ollama_status()
    if ollama_status:
        st.sidebar.markdown('<div class="status-box status-success">✅ ' + t('ollama_running') + '</div>', unsafe_allow_html=True)
        models = dali.list_available_models()
        if models:
            st.sidebar.selectbox(t('select_model'), models, key="selected_model")
        else:
            st.sidebar.warning(t('no_models_available'))
    else:
        st.sidebar.markdown('<div class="status-box status-error">❌ ' + t('ollama_not_running') + '</div>', unsafe_allow_html=True)
        st.sidebar.error(t('start_ollama'))
    
    # Check Firecrawl API
    if dali.firecrawl_api_key:
        st.sidebar.markdown('<div class="status-box status-success">✅ ' + t('firecrawl_configured') + '</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-box status-warning">⚠️ ' + t('firecrawl_not_configured') + '</div>', unsafe_allow_html=True)
        st.sidebar.info(t('set_firecrawl_key'))
    
    # Vector database status
    try:
        collection_count = st.session_state.dali_system.collection.count()
        st.sidebar.markdown('<div class="status-box status-success">✅ ' + t('vector_db_ready') + '</div>', unsafe_allow_html=True)
        st.sidebar.info(t('documents_in_db') + f": {collection_count}")
    except:
        st.sidebar.markdown('<div class="status-box status-error">❌ ' + t('vector_db_error') + '</div>', unsafe_allow_html=True)

def main_interface():
    """Main application interface"""
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ DALI Legal AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Development of Ambitious Leading Ideas @ Siyada Tech</p>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 " + t('chat'), "🌐 " + t('web_scraping'), "📚 " + t('document_management'), "📊 " + t('analytics')])
    
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
    st.markdown("## 💬 " + t('legal_ai_assistant'))
    st.markdown(t('ask_questions'))
    
    # Chat input
    user_question = st.text_input(
        t('ask_legal_question'),
        placeholder=t('ask_question_placeholder'),
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button(t('ask_question_button'), type="primary")
    with col2:
        clear_chat = st.button(t('clear_chat_history'))
    
    if clear_chat:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask_button and user_question:
        with st.spinner("Searching legal documents and generating response..."):
            # Get selected model
            selected_model = st.session_state.get("selected_model", "llama3.2:1b")
            
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
        st.markdown("### 📝 " + t('chat_history'))
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"Q: {chat['question']}", expanded=(i==0)):
                st.markdown(f"**{t('question')}:** {chat['question']}")
                st.markdown(f"**{t('answer')}:** {chat['answer']}")
                st.markdown(f"**{t('sources_used')}:** {chat['context_used']} documents")
                if chat['sources']:
                    st.markdown(f"**{t('source_details')}:**")
                    for source in chat['sources']:
                        st.json(source)
                st.markdown(f"*{t('asked_at')}: {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}*")

def web_scraping_interface():
    """Web scraping interface"""
    st.markdown("## 🌐 " + t('legal_web_scraping'))
    st.markdown(t('scrape_description'))
    
    # URL input
    url_to_scrape = st.text_input(
        t('enter_url'),
        placeholder=t('scrape_placeholder'),
        key="scrape_url"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        scrape_button = st.button(t('scrape_button'), type="primary")
    with col2:
        add_to_db = st.checkbox(t('add_to_kb'), value=True)
    
    if scrape_button and url_to_scrape:
        if not st.session_state.dali_system.firecrawl_api_key:
            st.error(t('firecrawl_not_configured_error'))
            return
        
        with st.spinner(t('scraping_website')):
            result = st.session_state.dali_system.scrape_with_firecrawl(url_to_scrape)
            
            if "error" in result:
                st.error(f"{t('scraping_failed')}: {result['error']}")
            else:
                st.success(t('website_scraped_successfully'))
                
                # Display scraped content
                if "data" in result and "markdown" in result["data"]:
                    content = result["data"]["markdown"]
                    st.markdown("### 📄 " + t('scraped_content_preview'))
                    st.text_area(t('content'), content[:1000] + "..." if len(content) > 1000 else content, height=200)
                    
                    if add_to_db:
                        # Add to vector database
                        metadata = {
                            "source": url_to_scrape,
                            "type": "web_scraped",
                            "scraped_at": datetime.now().isoformat(),
                            "title": result["data"].get("title", "Unknown")
                        }
                        
                        if st.session_state.dali_system.add_document_to_vectordb(content, metadata):
                            st.success(t('content_added_to_kb'))
                            st.session_state.documents_added += 1
                        else:
                            st.error(t('failed_to_add_content'))

def document_management_interface():
    """Document management interface"""
    st.markdown("## 📚 " + t('document_management'))
    st.markdown(t('upload_manage_documents'))
    
    # File upload
    uploaded_files = st.file_uploader(
        t('upload_legal_documents'),
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
                st.warning(t('pdf_processing_not_implemented'))
                continue
            else:
                st.error(f"{t('unsupported_file_type')}: {uploaded_file.type}")
                continue
            
            # Display content preview
            st.text_area(f"{t('content_preview')} - {uploaded_file.name}", content[:500] + "..." if len(content) > 500 else content, height=150)
            
            # Add to database button
            if st.button(f"{t('add_to_knowledge_base')} {uploaded_file.name}", key=f"add_{uploaded_file.name}"):
                metadata = {
                    "source": uploaded_file.name,
                    "type": "uploaded_document",
                    "uploaded_at": datetime.now().isoformat(),
                    "file_size": len(content)
                }
                
                if st.session_state.dali_system.add_document_to_vectordb(content, metadata):
                    st.success(f"✅ {uploaded_file.name} {t('added_to_kb')}")
                    st.session_state.documents_added += 1
                else:
                    st.error(f"❌ {t('failed_to_add_to_kb')} {uploaded_file.name}")
    
    # Document search
    st.markdown("### 🔍 " + t('search_documents'))
    search_query = st.text_input(t('search_in_kb'), key="doc_search")
    
    if search_query:
        with st.spinner(t('searching_documents')):
            results = st.session_state.dali_system.search_documents(search_query, n_results=10)
            
            if results:
                st.markdown(f"{t('found_documents')} {len(results)}:")
                for i, doc in enumerate(results):
                    with st.expander(f"{t('document')} {i+1} ({t('similarity')}: {1-doc['distance']:.3f})"):
                        st.markdown(f"**{t('content')}:** {doc['content'][:300]}...")
                        st.json(doc['metadata'])
            else:
                st.info(t('no_documents_found'))

def analytics_interface():
    """Analytics and system information"""
    st.markdown("## 📊 " + t('system_analytics'))
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(t('documents_added'), st.session_state.documents_added)
    
    with col2:
        try:
            total_docs = st.session_state.dali_system.collection.count()
            st.metric(t('total_documents'), total_docs)
        except:
            st.metric(t('total_documents'), "Error")
    
    with col3:
        st.metric(t('chat_sessions'), len(st.session_state.chat_history))
    
    with col4:
        models = st.session_state.dali_system.list_available_models()
        st.metric(t('available_models'), len(models))
    
    # Model information
    st.markdown("### 🤖 " + t('available_models_title'))
    models = st.session_state.dali_system.list_available_models()
    if models:
        model_df = pd.DataFrame({"Model Name": models})
        st.dataframe(model_df, use_container_width=True)
    else:
        st.info(t('no_models_available_install'))
    
    # Recent activity
    st.markdown("### 📈 " + t('recent_activity'))
    if st.session_state.chat_history:
        recent_chats = st.session_state.chat_history[-5:]  # Last 5 chats
        activity_data = []
        for chat in recent_chats:
            activity_data.append({
                t('timestamp'): chat["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                t('question'): chat["question"][:50] + "..." if len(chat["question"]) > 50 else chat["question"],
                t('sources_used_count'): chat["context_used"]
            })
        
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.info(t('no_recent_activity'))

def main():
    """Main application entry point"""
    initialize_session_state()
    display_system_status()
    main_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(t('footer_text'))

if __name__ == "__main__":
    main()

