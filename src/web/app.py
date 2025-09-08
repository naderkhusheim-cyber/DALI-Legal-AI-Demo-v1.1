"""
DALI Legal AI - Main Streamlit Web Application
ChatGPT-style interface for legal professionals
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import hashlib
import uuid
import streamlit.components.v1 as components
import requests

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

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    /* ChatGPT-like styling */
    .main-container {
        max-width: 100%;
        margin: 0 auto;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    .chat-container {
        flex: 1 1 auto;
        overflow-y: auto;
        padding: 0;
        background: transparent;
        margin: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 0;
    }
    
    .chat-container.empty {
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    .welcome-message {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2rem;
        margin: 2rem 0;
    }
    
    .message {
        margin-bottom: 1.5rem;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        line-height: 1.5;
    }
    
    .user-message {
        background: #10a37f;
        color: white;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background: #f7f7f8;
        color: #374151;
        margin-right: auto;
        margin-left: 0;
        border-bottom-left-radius: 4px;
        border: 1px solid #e5e5e5;
    }
    
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .chat-input-form {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .chat-input-field {
        flex: 1;
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 25px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        outline: none;
        transition: border-color 0.2s;
    }
    
    .chat-input-field:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
    }
    
    .chat-dropdown-button {
        background: #10a37f;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.2s;
        font-size: 1.2rem;
        position: relative;
    }
    
    .chat-dropdown-button:hover {
        background: #0d8a6b;
    }
    
    .chat-send-button {
        background: #10a37f;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .chat-send-button:hover {
        background: #0d8a6b;
    }
    
    .dropdown-menu {
        position: absolute;
        bottom: 100%;
        right: 0;
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        min-width: 200px;
        z-index: 1000;
        display: none;
    }
    
    .dropdown-menu.show {
        display: block;
    }
    
    .dropdown-item {
        padding: 0.75rem 1rem;
        cursor: pointer;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: background-color 0.2s;
    }
    
    .dropdown-item:hover {
        background: #f8f9fa;
    }
    
    .dropdown-item:last-child {
        border-bottom: none;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2c5f2d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .new-chat-btn {
        width: 100%;
        background: #007bff;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        cursor: pointer;
    }
    
    .chat-history-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        cursor: pointer;
        background: #f8f9fa;
        border-left: 3px solid transparent;
    }
    
    .chat-history-item:hover {
        background: #e9ecef;
        border-left-color: #007bff;
    }
    
    .chat-history-item.active {
        background: #e3f2fd;
        border-left-color: #007bff;
    }
    
    
    
    /* Overall page styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 25px;
        padding: 0.75rem 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Button styling - dark style for all buttons except chat input */
    .stButton > button {
        background: #222 !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 18px !important;
        padding: 6px 16px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        box-shadow: none !important;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: #333 !important;
        color: #fff !important;
    }
    /* Restore default style for Attach, Search, Study, Voice buttons */
    #attach_btn, #search_btn, #study_btn, #voice_btn {
        background: initial !important;
        color: initial !important;
        border: initial !important;
        border-radius: initial !important;
        padding: initial !important;
        font-weight: initial !important;
        font-size: initial !important;
        box-shadow: initial !important;
        transition: initial !important;
    }
    #attach_btn:hover, #search_btn:hover, #study_btn:hover, #voice_btn:hover {
        background: initial !important;
        color: initial !important;
    }
    /* Restore gradient style for Attach, Search, Study, Voice buttons */
    #attach_btn, #search_btn, #study_btn, #voice_btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 6px 16px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        transition: background 0.2s;
    }
    #attach_btn:hover, #search_btn:hover, #study_btn:hover, #voice_btn:hover {
        background: linear-gradient(135deg, #5a62d6 0%, #5e3b8a 100%) !important;
        color: #fff !important;
    }
    /* Chat input box - black style */
    .stTextInput > div > div > input {
        background: #111 !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 25px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        backdrop-filter: blur(10px);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    .upload-modal {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 1px solid #e5e5e5;
        margin: 2rem auto;
        max-width: 600px;
    }
</style>
""", unsafe_allow_html=True)

# Add a translation function and language toggle at the top of the page
LANGUAGES = {
    'en': {
        'attach': 'Attach',
        'search': 'Search',
        'study': 'Study',
        'voice': 'Voice',
        'send': 'Send',
        'ask_anything': 'Ask anything',
        'web_research': 'Web Research',
        'enter_query': 'Enter your search query:',
        'max_results': 'Max results',
        'add_to_kb': 'Add results to knowledge base',
        'cancel': 'Cancel',
        'back_to_chat': '← Back to Chat',
        'login': 'Login / Sign Up',
        'account': 'Account',
        'chat_history': 'Chat History',
        'no_chat_history': 'No chat history yet',
        'new_chat': 'New Chat',
        'welcome_title': '⚖️ Welcome to DALI Legal AI',
        'welcome_subtitle': 'Your intelligent legal assistant is ready to help with:',
        'welcome_bullet1': 'Legal research and analysis',
        'welcome_bullet2': 'Document review and insights',
        'welcome_bullet3': 'Contract analysis',
        'welcome_bullet4': 'Compliance guidance',
        'welcome_hint': 'Start by asking a question or uploading a document using the buttons below.',
        'upload_document': 'Upload Document',
        'choose_document': 'Choose a document',
        'drag_drop': 'Drag and drop file here',
        'file_limit': 'Limit 200MB per file • PDF, DOCX, TXT, MD',
        'what_do': 'What would you like to do?',
        'quick_analysis': 'Quick Analysis',
        'detailed_analysis': 'Detailed Analysis',
        'add_to_kb': 'Add to Knowledge Base',
        'both_analysis_kb': 'Both Analysis & Add to KB',
        'analysis_type': 'Analysis Type',
        'general': 'general',
        'contract': 'contract',
        'litigation': 'litigation',
        'compliance': 'compliance',
        'process_document': 'Process Document',
        'cancel': 'Cancel',
        'back_to_chat': '← Back to Chat',
        'welcome_user': 'Welcome, {user_name}!',
        'logout': 'Logout',
        'drag_drop_files': 'Drag and drop files',
        'new_chat': 'New Chat',
        'search': 'Search',
        'cancel': 'Cancel',
    },
    'ar': {
        'attach': 'إرفاق',
        'search': 'بحث',
        'study': 'دراسة',
        'voice': 'صوت',
        'send': 'إرسال',
        'ask_anything': 'اسأل أي شيء',
        'web_research': 'بحث ويب',
        'enter_query': 'أدخل استفسارك:',
        'max_results': 'أقصى عدد للنتائج',
        'add_to_kb': 'أضف النتائج إلى قاعدة المعرفة',
        'cancel': 'إلغاء',
        'back_to_chat': '← العودة للمحادثة',
        'login': 'تسجيل الدخول / إنشاء حساب',
        'account': 'الحساب',
        'chat_history': 'سجل المحادثات',
        'no_chat_history': 'لا يوجد سجل محادثات بعد',
        'new_chat': 'محادثة جديدة',
        'welcome_title': '⚖️ مرحبًا بك في دالي للذكاء الاصطناعي القانوني',
        'welcome_subtitle': 'مساعدك القانوني الذكي جاهز لمساعدتك في:',
        'welcome_bullet1': 'البحث والتحليل القانوني',
        'welcome_bullet2': 'مراجعة المستندات وتقديم الرؤى',
        'welcome_bullet3': 'تحليل العقود',
        'welcome_bullet4': 'إرشادات الامتثال',
        'welcome_hint': 'ابدأ بطرح سؤال أو تحميل مستند باستخدام الأزرار أدناه.',
        'upload_document': 'تحميل مستند',
        'choose_document': 'اختر مستندًا',
        'drag_drop': 'اسحب وأسقط الملف هنا',
        'file_limit': 'الحد الأقصى 200 ميجابايت لكل ملف • PDF, DOCX, TXT, MD',
        'what_do': 'ماذا تريد أن تفعل؟',
        'quick_analysis': 'تحليل سريع',
        'detailed_analysis': 'تحليل مفصل',
        'add_to_kb': 'أضف إلى قاعدة المعرفة',
        'both_analysis_kb': 'تحليل وإضافة إلى قاعدة المعرفة',
        'analysis_type': 'نوع التحليل',
        'general': 'عام',
        'contract': 'عقد',
        'litigation': 'تقاضي',
        'compliance': 'امتثال',
        'process_document': 'معالجة المستند',
        'cancel': 'إلغاء',
        'back_to_chat': '← العودة للمحادثة',
        'welcome_user': 'مرحبًا، {user_name}!',
        'logout': 'تسجيل الخروج',
        'drag_drop_files': 'اسحب وأسقط الملفات',
        'new_chat': 'محادثة جديدة',
        'search': 'بحث',
        'cancel': 'إلغاء',
    }
}
def t(key):
    lang = st.session_state.get('language', 'en')
    return LANGUAGES[lang].get(key, key)
# Language toggle button at the top right
lang = st.session_state.get('language', 'en')
lang_toggle_label = 'العربية' if lang == 'en' else 'English'
if st.button(lang_toggle_label, key='lang_toggle', help='Switch language', use_container_width=False):
    st.session_state.language = 'ar' if lang == 'en' else 'en'
    st.rerun()


class UserDatabase:
    """Simple user database using SQLite"""
    
    def __init__(self, db_path="data/users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, email, password_hash))
            
            conn.commit()
            return True, "User created successfully!"
            
        except sqlite3.IntegrityError:
            return False, "Username or email already exists!"
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, username, email, settings FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Update last login
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user[0],))
            conn.commit()
            conn.close()
            
            return True, {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'settings': json.loads(user[3]) if user[3] else {}
            }
        
        return False, "Invalid username or password"
    
    def update_user_settings(self, user_id, settings):
        """Update user settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET settings = ? WHERE id = ?
        ''', (json.dumps(settings), user_id))
        
        conn.commit()
        conn.close()


class DALIApp:
    """Main DALI Legal AI Application with ChatGPT-like interface"""
    
    def __init__(self):
        self.config = load_config()
        self.user_db = UserDatabase()
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
        
        # Ensure navigation has a default before any widget is created
        if 'navigation' not in st.session_state:
            st.session_state.navigation = "🏠 Dashboard"
        
        # ChatGPT-like state
        if 'current_chat_id' not in st.session_state:
            st.session_state.current_chat_id = None
        
        if 'chat_sessions' not in st.session_state:
            st.session_state.chat_sessions = {}
        
        if 'current_messages' not in st.session_state:
            st.session_state.current_messages = []
    
    def render_sidebar(self):
        """Render ChatGPT-like sidebar"""
        with st.sidebar:
            # Header
            st.markdown("""
            <div class="sidebar-header">
                <h2>⚖️ DALI</h2>
                <p>Legal AI Assistant</p>
                <small>دائرة أفكار رائدة مبتكرة</small>
            </div>
            """, unsafe_allow_html=True)
            
            # New Chat Button
            if st.button(t('new_chat'), key="new_chat", use_container_width=True):
                self.create_new_chat()
            
            # User Account Section
            st.markdown(f"### {t('account')}")
            if not hasattr(st.session_state, 'user_logged_in') or not st.session_state.user_logged_in:
                if st.button(t('login'), use_container_width=True):
                    st.session_state.show_login = True
                    st.rerun()
            else:
                st.success(t('welcome_user').format(user_name=st.session_state.get('user_name', '')))
                if st.button(t('account'), use_container_width=True):
                    st.session_state.show_settings = True
                    st.rerun()
                if st.button(t('logout'), use_container_width=True):
                    st.session_state.user_logged_in = False
                    st.session_state.user_name = None
                    st.rerun()
            
            
            
            # Chat History
            st.markdown(f"### {t('chat_history')}")
            if st.session_state.chat_sessions:
                for chat_id, session in st.session_state.chat_sessions.items():
                    title = session.get('title', f'Chat {chat_id[:8]}')
                    is_active = chat_id == st.session_state.current_chat_id
                    
                    if st.button(
                        title,
                        key=f"chat_{chat_id}",
                        help=f"Created: {session.get('created_at', 'Unknown')}",
                        use_container_width=True
                    ):
                        self.load_chat_session(chat_id)
            else:
                st.info(t('no_chat_history'))
    
    def create_new_chat(self):
        """Create a new chat session"""
        import uuid
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = chat_id
        st.session_state.current_messages = []
        st.session_state.chat_sessions[chat_id] = {
            'title': f'New Chat {len(st.session_state.chat_sessions) + 1}',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'messages': []
        }
        st.rerun()
    
    def load_chat_session(self, chat_id):
        """Load an existing chat session"""
        st.session_state.current_chat_id = chat_id
        if chat_id in st.session_state.chat_sessions:
            st.session_state.current_messages = st.session_state.chat_sessions[chat_id].get('messages', [])
        st.rerun()
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        # Restore: Show welcome message and center chat container if no messages
        if not st.session_state.current_messages:
            st.markdown('<div class="chat-container empty">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="welcome-message">
                <h2>{t('welcome_title')}</h2>
                <p>{t('welcome_subtitle')}</p>
                <ul style="text-align: left; display: inline-block; color: rgba(255, 255, 255, 0.7);">
                    <li>{t('welcome_bullet1')}</li>
                    <li>{t('welcome_bullet2')}</li>
                    <li>{t('welcome_bullet3')}</li>
                    <li>{t('welcome_bullet4')}</li>
                </ul>
                <p style="margin-top: 2rem; color: rgba(255, 255, 255, 0.6);">
                    {t('welcome_hint')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        # Display messages if present
        for message in st.session_state.current_messages:
            if message['role'] == 'user':
                st.markdown(f'''
                <div class="message user-message">
                    {message['content']}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="message assistant-message">
                    {message['content']}
                </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # Chat input remains at the bottom
        
        # Chat input
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        # Input form for text input and submit only
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                t('ask_anything'),
                placeholder=t('ask_anything'),
                label_visibility="collapsed",
                key="chat_input_field"
            )
            submitted = st.form_submit_button(t('send'), use_container_width=True)
        if user_input.strip() and submitted:
            self.process_user_message(user_input.strip())
        # Action buttons row (outside the form)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            attach_clicked = st.button(t('attach'), key="attach_btn", use_container_width=True)
        with col2:
            search_clicked = st.button(t('search'), key="search_btn", use_container_width=True)
        with col3:
            study_clicked = st.button(t('study'), key="study_btn", use_container_width=True)
        with col4:
            voice_clicked = st.button(t('voice'), key="voice_btn", use_container_width=True)
        # Handle action buttons
        if attach_clicked:
            st.session_state.show_upload_modal = True
            st.rerun()
        if search_clicked:
            st.session_state.chat_mode = 'web_research'
            st.rerun()
        if study_clicked:
            pass  # Implement study action if needed
        if voice_clicked:
            import streamlit.components.v1 as components
            components.html(
                '''
                <script>
                if (!window.hasVoiceListener) {
                    window.hasVoiceListener = true;
                    window.voiceToInput = function() {
                        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                            alert('Speech recognition not supported in this browser.');
                            return;
                        }
                        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        var recognition = new SpeechRecognition();
                        recognition.lang = 'ar-SA,en-US';
                        recognition.interimResults = false;
                        recognition.maxAlternatives = 1;
                        recognition.onresult = function(event) {
                            var transcript = event.results[0][0].transcript;
                            var input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                            if (input) {
                                input.value = transcript;
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        };
                        recognition.onerror = function(event) {
                            alert('Voice recognition error: ' + event.error);
                        };
                        recognition.start();
                    };
                    setTimeout(() => window.voiceToInput(), 100);
                } else {
                    window.voiceToInput();
                }
                </script>
                ''',
                height=0
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Upload Modal
        if hasattr(st.session_state, 'show_upload_modal') and st.session_state.show_upload_modal:
            self.render_upload_modal()
        
        # Web Search Modal
        if hasattr(st.session_state, 'show_web_search_modal') and st.session_state.show_web_search_modal:
            self.render_web_search_modal()
    
    def process_user_message(self, message):
        """Process user message and generate response"""
        if not hasattr(st.session_state, 'components_initialized') or not st.session_state.components_initialized:
            st.error("System not initialized. Please check configuration.")
            return
        # Numeral normalization for query
        def normalize_numerals(text):
            arabic_to_western = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
            western_to_arabic = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
            text = text.translate(arabic_to_western)
            text = text.translate(western_to_arabic)
            return text
        normalized_message = normalize_numerals(message)
        # Improved language detection
        def is_arabic(text):
            import re
            # True only if the majority of letters are Arabic
            arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
            total_letters = len(re.findall(r'[A-Za-z\u0600-\u06FF]', text))
            return arabic_chars > 0 and arabic_chars >= total_letters / 2
        def is_english(text):
            import re
            english_chars = len(re.findall(r'[A-Za-z]', text))
            total_letters = len(re.findall(r'[A-Za-z\u0600-\u06FF]', text))
            return english_chars > 0 and english_chars >= total_letters / 2
        # Prepend language instruction for LLM only
        llm_message = normalized_message
        if is_arabic(normalized_message):
            llm_message = (
                "أجب على هذا السؤال باللغة العربية فقط، حتى لو كان السياق أو المستندات باللغة الإنجليزية. لا تستخدم اللغة الإنجليزية في الإجابة.\n"
                + normalized_message
            )
        elif is_english(normalized_message):
            llm_message = (
                "Answer in English only, even if the context or documents are in Arabic.\n"
                + normalized_message
            )
        # Store only the original user message in chat history
        st.session_state.current_messages.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        # Generate response
        with st.spinner("DALI is thinking..."):
            try:
                # Search knowledge base for all relevant context (no n_results limit)
                kb_results = self.vector_store.search(normalized_message, n_results=None)  # None means all
                context = ""
                # Use language-matched context label
                if is_arabic(normalized_message):
                    context_label = 'مستند'
                elif is_english(normalized_message):
                    context_label = 'Document'
                else:
                    context_label = 'Document'
                # Optionally, filter context chunks to match question language (if possible)
                def chunk_language(text):
                    import re
                    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
                    english_chars = len(re.findall(r'[A-Za-z]', text))
                    if arabic_chars > english_chars:
                        return 'ar'
                    elif english_chars > arabic_chars:
                        return 'en'
                    else:
                        return 'unknown'
                if kb_results:
                    # Try to match context language to question
                    if is_arabic(normalized_message):
                        filtered = [r for r in kb_results if chunk_language(r['content']) == 'ar']
                        if not filtered:
                            filtered = kb_results
                    elif is_english(normalized_message):
                        filtered = [r for r in kb_results if chunk_language(r['content']) == 'en']
                        if not filtered:
                            filtered = kb_results
                    else:
                        filtered = kb_results
                    context = "\n\n".join([
                        f"{context_label}: {r['metadata'].get('title', 'Unknown')}\n{r['content'][:500]}..." for r in filtered
                    ])
                print("=== LLM CONTEXT ===\n", context)
                response = self.llm_engine.generate_response(
                    query=llm_message,
                    context=context if context else None
                )
                st.session_state.current_messages.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                if st.session_state.current_chat_id:
                    st.session_state.chat_sessions[st.session_state.current_chat_id]['messages'] = st.session_state.current_messages
                    if st.session_state.chat_sessions[st.session_state.current_chat_id]['title'].startswith('New Chat'):
                        st.session_state.chat_sessions[st.session_state.current_chat_id]['title'] = message[:30] + "..." if len(message) > 30 else message
                st.rerun()
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")
    
    def handle_document_upload(self):
        """Handle one-step document upload"""
        uploaded_file = st.file_uploader(
            t('choose_document'),
            type=['pdf', 'docx', 'txt', 'md'],
            key="one_step_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                action = st.selectbox(
                    t('what_do'),
                    [t('quick_analysis'), t('detailed_analysis'), t('add_to_kb'), t('both_analysis_kb')],
                    key="one_step_action"
                )
            
            with col2:
                analysis_type = st.selectbox(
                    t('analysis_type'),
                    [t('general'), t('contract'), t('litigation'), t('compliance')],
                    key="one_step_analysis_type"
                )
            
            if st.button(t('process_document'), type="primary"):
                document_text = self.doc_processor.process_file(uploaded_file)
                # Print/log the extracted text for debugging (especially for Arabic)
                print(f"=== EXTRACTED DOCUMENT TEXT ({uploaded_file.name}) ===\n", document_text[:1000])
                # Numeral normalization for document text
                def normalize_numerals(text):
                    # Convert Arabic-Indic numerals to Western and vice versa
                    arabic_to_western = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
                    western_to_arabic = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
                    # Normalize both ways for robustness
                    text = text.translate(arabic_to_western)
                    text = text.translate(western_to_arabic)
                    return text
                document_text = normalize_numerals(document_text)
                if document_text:
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button(t('add_to_kb'), type="primary"):
                            metadata = create_legal_document_metadata(
                                title=uploaded_file.name,
                                document_type=analysis_type,
                                source="uploaded_document",
                                date_created=datetime.now().isoformat()
                            )
                            # Add to knowledge base with normalized text
                            doc_ids = self.vector_store.add_document(document_text, metadata)
                            st.success(f"Document added to knowledge base with {len(doc_ids)} chunks")
                            st.rerun()
                
                with col4:
                    if st.button(t('cancel')):
                        st.session_state.show_upload_modal = False
                        st.rerun()
            else:
                if st.button(t('cancel')):
                    st.session_state.show_upload_modal = False
                    st.rerun()
    
    def render_upload_modal(self):
        """Render document upload modal"""
        with st.container():
            st.markdown('<div class="upload-modal">', unsafe_allow_html=True)
            st.markdown(f"### 📄 {t('upload_document')}")
            
            uploaded_file = st.file_uploader(
                t('choose_document'),
                type=['pdf', 'docx', 'txt', 'md'],
                key="modal_upload"
            )
            
            st.caption(t('drag_drop_files'))
            st.caption(t('file_limit'))

            if uploaded_file:
                col1, col2 = st.columns(2)
                with col1:
                    action = st.selectbox(
                        t('what_do'),
                        [t('quick_analysis'), t('detailed_analysis'), t('add_to_kb'), t('both_analysis_kb')],
                        key="upload_action"
                    )
                
                with col2:
                    analysis_type = st.selectbox(
                        t('analysis_type'),
                        [t('general'), t('contract'), t('litigation'), t('compliance')],
                        key="modal_analysis_type"
                    )
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.button(t('process_document'), type="primary"):
                        self.process_uploaded_document(uploaded_file, action, analysis_type)
                        st.session_state.show_upload_modal = False
                        st.rerun()
                
                with col4:
                    if st.button(t('cancel')):
                        st.session_state.show_upload_modal = False
                        st.rerun()
            else:
                if st.button(t('cancel')):
                    st.session_state.show_upload_modal = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    def process_uploaded_document(self, uploaded_file, action, analysis_type):
        """Process uploaded document based on selected action"""
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                document_text = self.doc_processor.process_file(uploaded_file)
                
                if document_text:
                    # Add to chat
                    if st.session_state.current_chat_id:
                        st.session_state.current_messages.append({
                            'role': 'assistant',
                            'content': f"📄 Processing document: **{uploaded_file.name}**\n\nAction: {action}\nAnalysis Type: {analysis_type}",
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Perform analysis if requested
                    if "Analysis" in action:
                        analysis_result = self.llm_engine.analyze_document(document_text, analysis_type)
                        
                        if st.session_state.current_chat_id:
                            st.session_state.current_messages.append({
                                'role': 'assistant',
                                'content': f"## Analysis Results for {uploaded_file.name}\n\n{analysis_result}",
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    # Add to knowledge base if requested
                    if "Knowledge Base" in action or action == "Both Analysis & Add to KB":
                        metadata = create_legal_document_metadata(
                            title=uploaded_file.name,
                            document_type=analysis_type,
                            source="uploaded_document",
                            date_created=datetime.now().isoformat()
                        )
                        
                        doc_ids = self.vector_store.add_document(document_text, metadata)
                        
                        if st.session_state.current_chat_id:
                            st.session_state.current_messages.append({
                                'role': 'assistant',
                                'content': f"✅ Document added to knowledge base with {len(doc_ids)} chunks",
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    st.success(f"Document '{uploaded_file.name}' processed successfully!")
                else:
                    st.error("Could not extract text from document")
                    
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
    
    def render_web_search_modal(self):
        """Render web search modal"""
        with st.container():
            st.markdown('<div class="upload-modal">', unsafe_allow_html=True)
            st.markdown(f"### 🌐 {t('web_research')}")
            
            search_query = st.text_input(
                t('enter_query'),
                placeholder=t('enter_query'),
                key="web_search_query"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                max_results = st.number_input(t('max_results'), 1, 10, 5)
            
            with col2:
                add_to_kb = st.checkbox(t('add_to_kb'), value=True)
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("Search", type="primary"):
                    if search_query.strip():
                        self.process_web_search(search_query.strip(), max_results, add_to_kb)
                        st.session_state.show_web_search_modal = False
                        st.rerun()
                    else:
                        st.warning("Please enter a search query")
            
            with col4:
                if st.button("Cancel"):
                    st.session_state.show_web_search_modal = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    def process_web_search(self, query, max_results, add_to_kb):
        """Process web search request and always append results to the current chat"""
        with st.spinner(f"Searching for: {query}..."):
            try:
                # For now, we'll use a simple search simulation
                # In a real implementation, you'd use Google Search API or similar
                if st.session_state.current_chat_id:
                    # Always append the web search result to the current chat
                    st.session_state.current_messages.append({
                        'role': 'assistant',
                        'content': f"🌐 **Web Search Results for:** {query}\n\n*Note: This is a demo. In production, this would search real web sources.*",
                        'timestamp': datetime.now().isoformat()
                    })
                
                st.success(f"Web search completed for: {query}")
                
            except Exception as e:
                st.error(f"Error during web search: {str(e)}")
    
    def render_login_signup(self):
        """Render login/signup interface"""
        st.markdown(f"### {t('account')}")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("#### Login to your account")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login", type="primary")
                
                if login_button:
                    if username and password:
                        success, result = self.user_db.authenticate_user(username, password)
                        if success:
                            st.session_state.user_logged_in = True
                            st.session_state.user_name = result['username']
                            st.session_state.user_id = result['id']
                            st.session_state.user_settings = result['settings']
                            st.session_state.show_login = False
                            st.success(f"Welcome back, {result['username']}!")
                            st.rerun()
                        else:
                            st.error(result)
                    else:
                        st.warning("Please fill in all fields")
        
        with tab2:
            st.markdown("#### Create a new account")
            with st.form("signup_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_button = st.form_submit_button("Sign Up", type="primary")
                
                if signup_button:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password == confirm_password:
                            success, result = self.user_db.create_user(new_username, new_email, new_password)
                            if success:
                                st.success(result)
                                st.info("Please login with your new account")
                            else:
                                st.error(result)
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.warning("Please fill in all fields")
        
        if st.button(t('back_to_chat')):
            st.session_state.show_login = False
            st.rerun()
    
    def render_user_settings(self):
        """Render user settings interface"""
        st.markdown(f"### ⚙️ {t('settings')}")
        
        if not hasattr(st.session_state, 'user_logged_in') or not st.session_state.user_logged_in:
            st.warning("Please login to access settings")
            return
        
        st.markdown(f"**Welcome, {st.session_state.user_name}!**")
        
        # LLM Settings
        with st.expander(f"🧠 {t('llm_engine_settings')}"):
            current_model = st.selectbox(
                f"Current Model",
                ["llama3", "mistral", "codellama"],
                index=0
            )
            
            temperature = st.slider("Response Temperature", 0.0, 1.0, 0.3)
            max_tokens = st.number_input("Max Response Tokens", 100, 4000, 2048)
            
            if st.button(f"Update {t('llm_settings')}"):
                # Save to user settings
                settings = st.session_state.get('user_settings', {})
                settings['llm'] = {
                    'model': current_model,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
                st.session_state.user_settings = settings
                self.user_db.update_user_settings(st.session_state.user_id, settings)
                st.success(f"{t('llm_settings')} updated!")
        
        # Data Management
        with st.expander(f"🗑️ {t('data_management')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Clear {t('chat_history')}", type="secondary"):
                    st.session_state.chat_sessions = {}
                    st.session_state.current_chat_id = None
                    st.session_state.current_messages = []
                    st.success(f"{t('chat_history')} cleared!")
            
            with col2:
                if st.button(f"Reset {t('knowledge_base')}", type="secondary"):
                    if st.checkbox(f"I understand this will delete all documents"):
                        try:
                            self.vector_store.reset_collection()
                            st.success(f"{t('knowledge_base')} reset successfully!")
                        except Exception as e:
                            st.error(f"Error resetting knowledge base: {str(e)}")
            # Debug: print VectorStore methods and import path
            print("VectorStore methods:", dir(self.vector_store))
            print("VectorStore imported from:", type(self.vector_store).__module__)
            # Show all documents in the knowledge base
            all_docs = self.vector_store.list_all_documents()
            if all_docs:
                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Title": d["title"],
                        "Type": d["type"],
                        "Source": d["source"],
                        "Content Preview": d["content_preview"],
                        "ID": d["id"]
                    } for d in all_docs
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No documents found in the knowledge base.")
        
        # Account Management
        with st.expander(f"👤 {t('account_management')}"):
            st.info(f"Username: {st.session_state.user_name}")
            st.info(f"User ID: {st.session_state.user_id}")
            
            if st.button(f"Delete {t('account')}", type="secondary"):
                st.warning(f"{t('account_deletion_not_implemented')}")
        
        if st.button(t('back_to_chat')):
            st.session_state.show_settings = False
            st.session_state.chat_mode = 'chat'
            st.rerun()
    
    def render_document_upload(self):
        """Render document upload interface"""
        st.header(f"📄 {t('document_upload')}")
        
        uploaded_files = st.file_uploader(
            f"Upload legal documents",
            type=['pdf', 'docx', 'txt', 'md'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.markdown(f"### {uploaded_file.name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    analysis_type = st.selectbox(
                        f"Analysis Type",
                        ["general", "contract", "litigation", "compliance"],
                        key=f"analysis_type_{uploaded_file.name}"
                    )
                
                with col2:
                    add_to_kb = st.checkbox(
                        f"Add to {t('knowledge_base')}",
                        key=f"add_kb_{uploaded_file.name}"
                    )
                
                if st.button(f"Analyze {uploaded_file.name}", key=f"analyze_{uploaded_file.name}"):
                    with st.spinner(f"Analyzing {uploaded_file.name}..."):
                        try:
                            document_text = self.doc_processor.process_file(uploaded_file)
                            
                            if document_text:
                                analysis_result = self.llm_engine.analyze_document(
                                    document_text, analysis_type
                                )
                                
                                st.markdown("#### Analysis Results")
                                st.markdown(analysis_result)
                                
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
                                
                                # Add to current chat
                                if st.session_state.current_chat_id:
                                    st.session_state.current_messages.append({
                                        'role': 'assistant',
                                        'content': f"Document '{uploaded_file.name}' analyzed:\n\n{analysis_result}",
                                        'timestamp': datetime.now().isoformat()
                                    })
                                
                            else:
                                st.error("Could not extract text from document")
                                
                        except Exception as e:
                            st.error(f"Error analyzing document: {str(e)}")
    
    def render_web_research(self):
        """Render web research interface"""
        st.header(f"🌐 {t('web_research')}")
        
        research_urls = st.text_area(
            f"Enter {t('urls_to_research')} (one per line):",
            placeholder=f"https://laws.boe.gov.sa\nhttps://www.moj.gov.sa",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_pages = st.number_input(f"Max pages per {t('site')}", 1, 50, 5)
        
        with col2:
            add_to_kb = st.checkbox(f"Add results to {t('knowledge_base')}", value=True)
        
        if st.button(f"🌐 Start {t('web_research')}", type="primary"):
            if research_urls.strip():
                urls = [url.strip() for url in research_urls.split('\n') if url.strip()]
                
                with st.spinner(f"Researching {len(urls)} {t('sites')}..."):
                    try:
                        all_results = []
                        
                        for url in urls:
                            st.write(f"Researching: {url}")
                            
                            result = self.scraper.scrape_url(url)
                            
                            if result.success:
                                all_results.append(result)
                                
                                with st.expander(f"Results from {url}"):
                                    st.write(f"**Title:** {result.title}")
                                    st.write(f"**Content Preview:** {result.content[:500]}...")
                                
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
                            st.success(f"Successfully researched {len(all_results)} {t('sites')}!")
                            
                            # Add summary to current chat
                            if st.session_state.current_chat_id:
                                summary = f"Web research completed on {len(urls)} URLs. Found {len(all_results)} successful results."
                                st.session_state.current_messages.append({
                                    'role': 'assistant',
                                    'content': summary,
                                    'timestamp': datetime.now().isoformat()
                                })
                        
                    except Exception as e:
                        st.error(f"Error during web research: {str(e)}")
            else:
                st.warning(f"Please enter at least one {t('url')} to research.")
    
    def run(self):
        """Run the main application"""
        try:
            # Render sidebar
            self.render_sidebar()
            # Check if components are initialized
            if not hasattr(st.session_state, 'components_initialized') or not st.session_state.components_initialized:
                st.error("System initialization failed. Please check the configuration and try again.")
                return
            
            # Health checks for LLM and Firecrawl
            try:
                llm_engine = self.llm_engine if hasattr(self, 'llm_engine') else None
                if llm_engine:
                    healthy = llm_engine.health_check()
                    print(f"[Ollama Health Check] Model: {llm_engine.model_name}, Host: {llm_engine.host}, Port: {llm_engine.port}, Healthy: {healthy}")
                    if not healthy:
                        st.warning(f"⚠️ Ollama is not running or not responding at {llm_engine.host}:{llm_engine.port} (model: {llm_engine.model_name})")
                else:
                    st.warning("⚠️ LLM Engine is not initialized.")
            except Exception as e:
                print(f"[Ollama Health Check Error] {e}")
                st.warning(f"⚠️ Ollama health check failed: {e}")

            # Firecrawl health check
            try:
                firecrawl = self.scraper if hasattr(self, 'scraper') else None
                if firecrawl:
                    firecrawl_healthy = firecrawl.health_check()
                    print(f"[Firecrawl Health Check] API Key: {getattr(firecrawl, 'api_key', None)}, Healthy: {firecrawl_healthy}")
                    if not firecrawl_healthy:
                        st.warning("⚠️ Firecrawl is not available or not responding. Check your API key and network connection.")
                else:
                    st.warning("⚠️ Firecrawl Scraper is not initialized.")
            except Exception as e:
                print(f"[Firecrawl Health Check Error] {e}")
                st.warning(f"⚠️ Firecrawl health check failed: {e}")

            # Main content area
            if hasattr(st.session_state, 'show_login') and st.session_state.show_login:
                self.render_login_signup()
            elif hasattr(st.session_state, 'show_settings') and st.session_state.show_settings:
                self.render_user_settings()
            elif hasattr(st.session_state, 'show_document_upload') and st.session_state.show_document_upload:
                self.render_document_upload()
                if st.button(t('back_to_chat')):
                    st.session_state.show_document_upload = False
                    st.rerun()
            elif st.session_state.get('chat_mode', 'chat') == 'web_research':
                self.render_web_search_modal()
                if st.button(t("cancel"), key="cancel_web_research"):
                    st.session_state.chat_mode = 'chat'
                    st.rerun()
            else:
                # Main chat interface
                self.render_chat_interface()
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    # Initialize and run the application
    app = DALIApp()
    app.run()