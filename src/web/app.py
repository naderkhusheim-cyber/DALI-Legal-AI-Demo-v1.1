"""
DALI Legal AI - Main FastAPI Web Application
ChatGPT-style interface for legal professionals (migrated from Streamlit)
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import hashlib
import uuid
import requests
import numpy as np
import mysql.connector
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Body, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import tempfile
import re
import asyncio

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.llm_engine import LLMEngine
from core.vector_store import VectorStore, MySQLVectorStore, create_legal_document_metadata
from scrapers.firecrawl_scraper import FirecrawlScraper
from utils.document_processor import DocumentProcessor
from utils.config import load_config, get_mysql_config

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="src/web/templates")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_store = MySQLVectorStore(get_mysql_config())
doc_processor = DocumentProcessor()
vector_store = VectorStore()
scraper = FirecrawlScraper()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
# st.set_page_config(
#     page_title="DALI Legal AI",
#     page_icon="⚖️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Custom CSS for ChatGPT-like interface
# st.markdown("""
# <style>
#     /* ChatGPT-like styling */
#     .main-container {
#         max-width: 100%;
#         margin: 0 auto;
#         height: 100vh;
#         display: flex;
#         flex-direction: column;
#     }
    
#     .chat-container {
#         flex: 1 1 auto;
#         overflow-y: auto;
#         padding: 0;
#         background: transparent;
#         margin: 0;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         align-items: center;
#         min-height: 0;
#     }
    
#     .chat-container.empty {
#         justify-content: center;
#         align-items: center;
#         height: 100%;
#     }
    
#     .welcome-message {
#         text-align: center;
#         color: rgba(255, 255, 255, 0.8);
#         font-size: 1.2rem;
#         margin: 2rem 0;
#     }
    
#     .message {
#         margin-bottom: 1.5rem;
#         padding: 1rem 1.5rem;
#         border-radius: 18px;
#         max-width: 80%;
#         word-wrap: break-word;
#         line-height: 1.5;
#     }
    
#     .user-message {
#         background: #10a37f;
#         color: white;
#         margin-left: auto;
#         margin-right: 0;
#         border-bottom-right-radius: 4px;
#     }
    
#     .assistant-message {
#         background: #f7f7f8;
#         color: #374151;
#         margin-right: auto;
#         margin-left: 0;
#         border-bottom-left-radius: 4px;
#         border: 1px solid #e5e5e5;
#     }
    
#     .chat-input-container {
#         position: fixed;
#         bottom: 0;
#         left: 0;
#         right: 0;
#         background: rgba(255, 255, 255, 0.95);
#         padding: 1rem;
#         border-top: 1px solid rgba(0, 0, 0, 0.1);
#         backdrop-filter: blur(10px);
#         z-index: 1000;
#         box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
#     }
    
#     .chat-input-form {
#         max-width: 800px;
#         margin: 0 auto;
#         display: flex;
#         gap: 0.5rem;
#         align-items: center;
#     }
    
#     .chat-input-field {
#         flex: 1;
#         background: white;
#         border: 1px solid #d1d5db;
#         border-radius: 25px;
#         padding: 0.75rem 1rem;
#         font-size: 1rem;
#         outline: none;
#         transition: border-color 0.2s;
#     }
    
#     .chat-input-field:focus {
#         border-color: #10a37f;
#         box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
#     }
    
#     .chat-dropdown-button {
#         background: #10a37f;
#         color: white;
#         border: none;
#         border-radius: 50%;
#         width: 40px;
#         height: 40px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         cursor: pointer;
#         transition: background-color 0.2s;
#         font-size: 1.2rem;
#         position: relative;
#     }
    
#     .chat-dropdown-button:hover {
#         background: #0d8a6b;
#     }
    
#     .chat-send-button {
#         background: #10a37f;
#         color: white;
#         border: none;
#         border-radius: 25px;
#         padding: 0.75rem 1.5rem;
#         font-weight: 500;
#         cursor: pointer;
#         transition: background-color 0.2s;
#     }
    
#     .chat-send-button:hover {
#         background: #0d8a6b;
#     }
    
#     .dropdown-menu {
#         position: absolute;
#         bottom: 100%;
#         right: 0;
#         background: white;
#         border: 1px solid #e5e5e5;
#         border-radius: 8px;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
#         min-width: 200px;
#         z-index: 1000;
#         display: none;
#     }
    
#     .dropdown-menu.show {
#         display: block;
#     }
    
#     .dropdown-item {
#         padding: 0.75rem 1rem;
#         cursor: pointer;
#         border-bottom: 1px solid #f0f0f0;
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#         transition: background-color 0.2s;
#     }
    
#     .dropdown-item:hover {
#         background: #f8f9fa;
#     }
    
#     .dropdown-item:last-child {
#         border-bottom: none;
#     }
    
#     .sidebar-header {
#         background: linear-gradient(135deg, #1f4e79 0%, #2c5f2d 100%);
#         color: white;
#         padding: 1rem;
#         border-radius: 10px;
#         margin-bottom: 1rem;
#         text-align: center;
#     }
    
#     .new-chat-btn {
#         width: 100%;
#         background: #007bff;
#         color: white;
#         border: none;
#         padding: 0.75rem;
#         border-radius: 8px;
#         margin-bottom: 1rem;
#         cursor: pointer;
#     }
    
#     .chat-history-item {
#         padding: 0.5rem;
#         margin: 0.25rem 0;
#         border-radius: 5px;
#         cursor: pointer;
#         background: #f8f9fa;
#         border-left: 3px solid transparent;
#     }
    
#     .chat-history-item:hover {
#         background: #e9ecef;
#         border-left-color: #007bff;
#     }
    
#     .chat-history-item.active {
#         background: #e3f2fd;
#         border-left-color: #007bff;
#     }
    
    
    
#     /* Overall page styling */
#     .stApp {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         min-height: 100vh;
#     }
    
#     .main .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#         max-width: 100%;
#     }
    
#     /* Sidebar styling */
#     .css-1d391kg {
#         background: rgba(255, 255, 255, 0.95);
#         backdrop-filter: blur(10px);
#         border-right: 1px solid rgba(0, 0, 0, 0.1);
#     }
    
#     /* Input field styling */
#     .stTextInput > div > div > input {
#         background: rgba(255, 255, 255, 0.9);
#         border: 1px solid rgba(0, 0, 0, 0.1);
#         border-radius: 25px;
#         padding: 0.75rem 1rem;
#         backdrop-filter: blur(10px);
#     }
    
#     /* Button styling - dark style for all buttons except chat input */
#     .stButton > button {
#         background: #222 !important;
#         color: #fff !important;
#         border: 1px solid #444 !important;
#         border-radius: 18px !important;
#         padding: 6px 16px !important;
#         font-weight: 500 !important;
#         font-size: 1rem !important;
#         box-shadow: none !important;
#         transition: background 0.2s;
#     }
#     .stButton > button:hover {
#         background: #333 !important;
#         color: #fff !important;
#     }
#     /* Restore default style for Attach, Search, Study, Voice buttons */
#     #attach_btn, #search_btn, #study_btn, #voice_btn {
#         background: initial !important;
#         color: initial !important;
#         border: initial !important;
#         border-radius: initial !important;
#         padding: initial !important;
#         font-weight: initial !important;
#         font-size: initial !important;
#         box-shadow: initial !important;
#         transition: initial !important;
#     }
#     #attach_btn:hover, #search_btn:hover, #study_btn:hover, #voice_btn:hover {
#         background: initial !important;
#         color: initial !important;
#     }
#     /* Restore gradient style for Attach, Search, Study, Voice buttons */
#     #attach_btn, #search_btn, #study_btn, #voice_btn {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
#         color: #fff !important;
#         border: none !important;
#         border-radius: 18px !important;
#         padding: 6px 16px !important;
#         font-weight: 500 !important;
#         font-size: 1rem !important;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
#         transition: background 0.2s;
#     }
#     #attach_btn:hover, #search_btn:hover, #study_btn:hover, #voice_btn:hover {
#         background: linear-gradient(135deg, #5a62d6 0%, #5e3b8a 100%) !important;
#         color: #fff !important;
#     }
#     /* Chat input box - black style */
#     .stTextInput > div > div > input {
#         background: #111 !important;
#         color: #fff !important;
#         border: 1px solid #444 !important;
#         border-radius: 25px !important;
#         padding: 0.75rem 1rem !important;
#         font-size: 1rem !important;
#         backdrop-filter: blur(10px);
#     }
    
#     /* Selectbox styling */
#     .stSelectbox > div > div {
#         background: rgba(255, 255, 255, 0.9);
#         border: 1px solid rgba(0, 0, 0, 0.1);
#         border-radius: 10px;
#         backdrop-filter: blur(10px);
#     }

#     .upload-modal {
#         background: #f8f9fa;
#         padding: 1.5rem;
#         border-radius: 12px;
#         box-shadow: 0 4px 16px rgba(0,0,0,0.08);
#         border: 1px solid #e5e5e5;
#         margin: 2rem auto;
#         max-width: 600px;
#     }
# </style>
# """, unsafe_allow_html=True)

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
    lang = "en" # Default to English
    return LANGUAGES[lang].get(key, key)
# Language toggle button at the top right
lang = "en" # Default to English
lang_toggle_label = 'العربية' if lang == 'en' else 'English'
# if st.button(lang_toggle_label, key='lang_toggle', help='Switch language', use_container_width=False):
#     st.session_state.language = 'ar' if lang == 'en' else 'en'
#     st.rerun()


# Remove the entire UserDatabase class and all references to it, including instantiation and method calls.


class DALIApp:
    """Main DALI Legal AI Application with ChatGPT-like interface"""
    
    def __init__(self):
        self.config = load_config()
        self.initialize_components()
        self.initialize_session_state()
    
    def initialize_components(self):
        """Initialize AI components"""
        try:
            # Use model from session state if set, else from config
            model_name = "llama3:8b" # Default to a known model
            self.llm_engine = LLMEngine(
                model_name=model_name,
                host=self.config.get('ollama', {}).get('host', 'localhost'),
                port=self.config.get('ollama', {}).get('port', 11434)
            )
            # VectorStore should always use a valid local embedding model, never the selected LLM model
            embedding_model = self.config.get('chroma', {}).get('embedding_model', 'paraphrase-multilingual-MiniLM-L12-v2')
            self.vector_store = VectorStore(
                persist_directory=self.config.get('chroma', {}).get('persist_directory', './data/embeddings'),
                collection_name=self.config.get('chroma', {}).get('collection_name', 'legal_documents'),
                embedding_model=embedding_model
            )
            
            # Initialize Web Scraper
            self.scraper = FirecrawlScraper(
                api_key=self.config.get('firecrawl', {}).get('api_key')
            )
            
            # Initialize Document Processor
            self.doc_processor = DocumentProcessor()
            
            self.mysql_vector_store = MySQLVectorStore(get_mysql_config())
            
            # st.session_state.components_initialized = True # Removed st.session_state
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            # st.session_state.components_initialized = False # Removed st.session_state
            # st.session_state.initialization_error = str(e) # Removed st.session_state
    
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
    
    def mysql_authenticate_user(self, username, password):
        """Authenticate user against MySQL users table"""
        try:
            conn = mysql.connector.connect(**get_mysql_config())
            cursor = conn.cursor(dictionary=True)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('SELECT * FROM users WHERE username = %s AND password_hash = %s', (username, password_hash))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                if not user.get('is_active', False):
                    return False, "Account not activated. Please wait for admin approval."
                # Parse settings if present
                settings = {}
                if 'settings' in user and user['settings']:
                    try:
                        settings = json.loads(user['settings'])
                    except Exception:
                        settings = {}
                user_dict = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user.get('role', 'user'),
                    'is_active': user.get('is_active', False),
                    'settings': settings
                }
                return True, user_dict
            else:
                return False, "Invalid username or password."
        except Exception as e:
            return False, f"Database error: {e}"
    
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
                if st.session_state.get('user_role') == 'admin':
                    if st.button('Admin Dashboard', use_container_width=True):
                        st.session_state.show_admin_dashboard = True
                        st.rerun()
                if st.button(t('logout'), use_container_width=True):
                    st.session_state.user_logged_in = False
                    st.session_state.user_name = None
                    st.session_state.user_id = None
                    st.session_state.user_is_active = False
                    st.session_state.user_role = None
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
        print("=== LLM PROMPT ===\n", llm_message)
        # Store only the original user message in chat history
        st.session_state.current_messages.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        # Use MySQLVectorStore for per-user search
        user_id = self.get_current_user_id()
        if user_id:
            # Generate embedding for the query
            query_embedding = self.vector_store._generate_embedding(message)
            kb_results = self.mysql_vector_store.search_documents(user_id, query_embedding, top_k=20)
            context = ""
            if kb_results:
                context = "\n\n".join([
                    f"Document: {r['title']}\n{r['content'][:500]}..." for r in kb_results
                ])
            print("=== LLM CONTEXT (MySQL) ===\n", context)
            response = self.llm_engine.generate_response(
                query=llm_message,
                context=context if context else None
            )
            st.session_state.current_messages.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            # AI-generated chat title after first user message
            if st.session_state.current_chat_id and len(st.session_state.current_messages) == 2:
                # Only generate title after first user message
                try:
                    title_prompt = f"Generate a concise chat title (max 7 words) for this legal question: '{message}'"
                    chat_title = self.llm_engine.generate_response(query=title_prompt)
                    if chat_title:
                        st.session_state.chat_sessions[st.session_state.current_chat_id]['title'] = chat_title.strip()
                except Exception as e:
                    print(f"[ERROR] Failed to generate chat title: {e}")
            else:
                # Fallback: use first 30 chars of message
                if st.session_state.current_chat_id and st.session_state.chat_sessions[st.session_state.current_chat_id]['title'].startswith('New Chat'):
                    st.session_state.chat_sessions[st.session_state.current_chat_id]['title'] = message[:30] + "..." if len(message) > 30 else message
                st.rerun()
        else:
            st.error("No user logged in.")
    
    def handle_document_upload(self):
        uploaded_file = st.file_uploader(
            t('choose_document'),
            type=['pdf', 'docx', 'txt', 'md'],
            key="one_step_upload"
        )
        if uploaded_file:
            document_text = self.doc_processor.process_file(uploaded_file)
            # Numeral normalization for document text
            def normalize_numerals(text):
                arabic_to_western = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
                western_to_arabic = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
                text = text.translate(arabic_to_western)
                text = text.translate(western_to_arabic)
                return text
            document_text = normalize_numerals(document_text)
            if document_text:
                col3, col4 = st.columns(2)
                with col3:
                    if st.button(t('add_to_kb'), type="primary"):
                        user_id = self.get_current_user_id()
                        print(f"[DEBUG] user_id for upload: {user_id}")
                        if not user_id:
                            st.error("No user logged in.")
                            return
                        from core.vector_store import create_legal_document_metadata
                        import json
                        metadata = create_legal_document_metadata(
                            title=uploaded_file.name,
                            document_type="uploaded",
                            source="uploaded_document",
                            date_created=datetime.now().isoformat()
                        )
                        print(f"[DEBUG] Document metadata: {metadata}")
                        chunks = self.vector_store.text_splitter.split_text(document_text)
                        success_count = 0
                        for i, chunk in enumerate(chunks):
                            chunk_metadata = metadata.copy()
                            chunk_metadata['chunk_index'] = i
                            chunk_metadata['total_chunks'] = len(chunks)
                            embedding = self.vector_store._generate_embedding(chunk)
                            try:
                                self.mysql_vector_store.add_document(
                                    user_id=user_id,
                                    title=uploaded_file.name,
                                    document_type="uploaded",
                                    source="uploaded_document",
                                    content=chunk,
                                    embedding=np.array(embedding, dtype=np.float32),
                                    metadata=chunk_metadata
                                )
                                success_count += 1
                            except Exception as e:
                                print(f"[ERROR] Failed to add document chunk {i}: {e}")
                                st.error(f"Failed to add document chunk {i}: {e}")
                        if success_count == len(chunks):
                            st.success(f"Document added to knowledge base with {len(chunks)} chunks (MySQL)")
                        else:
                            st.error(f"Only {success_count} out of {len(chunks)} chunks were added. Check logs for details.")
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
                        user_id = self.get_current_user_id()
                        if not user_id:
                            st.error("No user logged in.")
                            return
                        metadata = create_legal_document_metadata(
                            title=uploaded_file.name,
                            document_type=analysis_type,
                            source="uploaded_document",
                            date_created=datetime.now().isoformat()
                        )
                        chunks = self.vector_store.text_splitter.split_text(document_text)
                        success_count = 0
                        for i, chunk in enumerate(chunks):
                            chunk_metadata = metadata.copy()
                            chunk_metadata['chunk_index'] = i
                            chunk_metadata['total_chunks'] = len(chunks)
                            embedding = self.vector_store._generate_embedding(chunk)
                            try:
                                self.mysql_vector_store.add_document(
                                    user_id=user_id,
                                    title=uploaded_file.name,
                                    document_type=analysis_type,
                                    source="uploaded_document",
                                    content=chunk,
                                    embedding=np.array(embedding, dtype=np.float32),
                                    metadata=chunk_metadata
                                )
                                success_count += 1
                            except Exception as e:
                                print(f"[ERROR] Failed to add document chunk {i}: {e}")
                                st.error(f"Failed to add document chunk {i}: {e}")
                        if success_count == len(chunks):
                            st.success(f"Document added to knowledge base with {len(chunks)} chunks (MySQL)")
                        else:
                            st.error(f"Only {success_count} out of {len(chunks)} chunks were added. Check logs for details.")
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
                        success, result = self.mysql_authenticate_user(username, password)
                        if success:
                            st.session_state.user_logged_in = True
                            st.session_state.user_name = result['username']
                            st.session_state.user_id = result['id']
                            st.session_state.user_settings = result['settings']
                            st.session_state.user_is_active = result.get('is_active', True)
                            st.session_state.user_role = result.get('role', 'user')
                            st.session_state.show_login = False
                            st.session_state.chat_mode = 'chat' # Set chat mode after successful login
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
                            success, result = self.mysql_create_user(new_username, new_email, new_password)
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
        # Debug: print session state for diagnosis
        st.write("Session state (debug):", {
            'user_logged_in': st.session_state.get('user_logged_in'),
            'user_is_active': st.session_state.get('user_is_active'),
            'user_name': st.session_state.get('user_name'),
            'user_id': st.session_state.get('user_id'),
            'user_role': st.session_state.get('user_role'),
        })
        if not self.is_user_logged_in_and_active():
            st.warning("Please login to access settings")
            return
        
        st.markdown(f"**Welcome, {st.session_state.user_name}!**")
        
        # LLM Settings
        with st.expander(f"🧠 {t('llm_engine_settings')}"):
            # Model selection dropdown
            available_models = [
                "llama3:8b",
                "llama3:latest",
                "mistral",
                "gpt-4o",
                "gpt-5"
            ]
            current_model = st.session_state.get('selected_llm_model', self.config.get('ollama', {}).get('model', 'llama3:8b'))
            selected_model = st.selectbox(
                "Select LLM Model",
                available_models,
                index=available_models.index(current_model) if current_model in available_models else 0
            )
            temperature = st.slider("Response Temperature", 0.0, 1.0, 0.3)
            max_tokens = st.number_input("Max Response Tokens", 100, 4000, 2048)
            if st.button(f"Update {t('llm_settings')}"):
                st.session_state.selected_llm_model = selected_model
                # Re-initialize LLM engine with new model
                self.llm_engine = LLMEngine(
                    model_name=selected_model,
                    host=self.config.get('ollama', {}).get('host', 'localhost'),
                    port=self.config.get('ollama', {}).get('port', 11434)
                )
                settings = st.session_state.get('user_settings', {})
                settings['llm'] = {
                    'model': selected_model,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
                st.session_state.user_settings = settings
                self.mysql_update_user_settings(st.session_state.user_id, settings)
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
            # Show all documents in the knowledge base (MySQL, current user)
            all_docs = self.list_documents_for_current_user()
            if all_docs:
                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Title": d["title"],
                        "Type": d["document_type"],
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
    
    def render_admin_dashboard(self):
        """Render the admin dashboard page (user management)"""
        st.markdown("# 🛡️ Admin Dashboard")
        st.markdown("## User Management")
        # Fetch all users from MySQL
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, username, email, role, is_active, created_at FROM users')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        import pandas as pd
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True)
        # Activate/deactivate/delete users and control allowed models
        for user in users:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            with col1:
                st.write(f"{user['username']} ({user['email']})")
            with col2:
                st.write(f"Role: {user['role']}")
            with col3:
                if user['role'] != 'admin':
                    if user['is_active']:
                        if st.button(f"Deactivate {user['username']}", key=f"deact_{user['id']}"):
                            self.set_user_active_status(user['id'], False)
                            st.success(f"Deactivated {user['username']}")
                            st.rerun()
                    else:
                        if st.button(f"Activate {user['username']}", key=f"act_{user['id']}"):
                            self.set_user_active_status(user['id'], True)
                            st.success(f"Activated {user['username']}")
                            st.rerun()
            with col4:
                if user['role'] != 'admin':
                    if st.button(f"Delete {user['username']}", key=f"del_{user['id']}"):
                        if st.confirm(f"Are you sure you want to delete {user['username']}? This cannot be undone.", key=f"confirm_del_{user['id']}"):
                            self.delete_user(user['id'])
                            st.success(f"Deleted {user['username']}")
                            st.rerun()
            with col5:
                # Allowed LLM models dropdown
                allowed_models = ["llama3:8b", "mistral", "gpt-4o", "gpt-3.5-turbo"]
                # Load user settings
                user_settings = {}
                try:
                    if 'settings' in user and user['settings']:
                        user_settings = json.loads(user['settings'])
                except Exception:
                    user_settings = {}
                current_allowed = user_settings.get('allowed_llm_models', allowed_models)
                selected_models = st.multiselect(f"Allowed Models for {user['username']}", allowed_models, default=current_allowed, key=f"allowed_models_{user['id']}")
                if selected_models != current_allowed:
                    user_settings['allowed_llm_models'] = selected_models
                    self.update_user_settings(user['id'], user_settings)
                    st.success(f"Updated allowed models for {user['username']}")
                    st.rerun()
        st.markdown("---")
        # Activity log (simple)
        st.markdown("## Activity Log (last 100 events)")
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 100''')
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        if logs:
            import pandas as pd
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("No activity log entries yet.")
        if st.button("Back to Chat"):
            st.session_state.show_admin_dashboard = False
            st.rerun()

    def set_user_active_status(self, user_id, is_active):
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = %s WHERE id = %s', (is_active, user_id))
        conn.commit()
        cursor.close()
        conn.close()

    def list_documents_for_current_user(self):
        """Return all documents for the current user from MySQL."""
        user_id = st.session_state.get('user_id')
        if not user_id:
            return []
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, title, document_type, source, LEFT(content, 200) AS content_preview FROM documents WHERE user_id = %s', (user_id,))
        docs = cursor.fetchall()
        cursor.close()
        conn.close()
        return docs

    def is_user_logged_in_and_active(self):
        return bool(st.session_state.get('user_logged_in')) and bool(st.session_state.get('user_is_active'))

    def get_current_user_id(self):
        if self.is_user_logged_in_and_active():
            return st.session_state.get('user_id')
        return None

    def render_user_chat_widget(self):
        """Render the user-to-user chat pop-up widget (true floating, improved UX, Streamlit-native only)"""
        import streamlit as st
        import time
        # Track unread messages for chat notification
        if 'unread_user_chat' not in st.session_state:
            st.session_state.unread_user_chat = {}
        # When chat popup is closed, count unread messages
        if not st.session_state.get('show_user_chat', False):
            conn = mysql.connector.connect(**get_mysql_config())
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM user_chats WHERE receiver_id = %s AND sender_id != %s AND sent_at > IFNULL(%s, '1970-01-01')''', (st.session_state.user_id, st.session_state.user_id, st.session_state.get('last_user_chat_open')))
            unread = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            st.session_state.unread_user_chat['count'] = unread
            print(f"[DEBUG] Unread user chat count: {unread}")
        # Show badge on chat icon if unread
        chat_icon_css = '''
        <style>
        .stChatIconBtn {
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            border-radius: 50%;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.2rem;
            z-index: 9999;
            cursor: pointer;
            border: none;
        }
        .chat-badge {
            position: absolute;
            top: 8px;
            right: 8px;
            background: #e74c3c;
            color: #fff;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            font-weight: bold;
            z-index: 10000;
        }
        </style>
        '''
        st.markdown(chat_icon_css, unsafe_allow_html=True)
        chat_icon_container = st.empty()
        with chat_icon_container.container():
            if st.button('💬', key='user_chat_fab', help='Open User Chat', use_container_width=False):
                st.session_state.show_user_chat = True
                st.session_state.last_user_chat_open = datetime.now().isoformat()
                st.session_state.unread_user_chat['count'] = 0
                st.rerun()
            if st.session_state.unread_user_chat.get('count', 0) > 0:
                st.markdown(f'<div class="chat-badge">{st.session_state.unread_user_chat["count"]}</div>', unsafe_allow_html=True)
        # Show the chat popup if active
        if st.session_state.get('show_user_chat', False):
            st.markdown('<div id="user-chat-popup" style="position: fixed; bottom: 110px; right: 32px; width: 370px; background: #fff; border-radius: 16px; box-shadow: 0 2px 16px rgba(0,0,0,0.18); padding: 1.2rem 1rem 1rem 1rem; z-index: 10000;">', unsafe_allow_html=True)
            st.markdown('### 👤 User Chat')
            # User search with dropdown
            search_username = st.text_input('Search user by username', key='user_search_input')
            found_users = []
            if search_username:
                conn = mysql.connector.connect(**get_mysql_config())
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT id, username FROM users WHERE username LIKE %s AND is_active=1', (f'%{search_username}%',))
                found_users = cursor.fetchall()
                cursor.close()
                conn.close()
            user_options = [(u['id'], u['username']) for u in found_users if u['id'] != st.session_state.get('user_id')]
            selected_user = None
            if user_options:
                selected_idx = st.selectbox('Select user to chat', list(range(len(user_options))), format_func=lambda i: user_options[i][1], key='user_chat_select')
                selected_user = user_options[selected_idx]
                if st.button(f"Start chat with {selected_user[1]}", key=f"start_chat_{selected_user[0]}"):
                    st.session_state.user_chat_partner_id = selected_user[0]
                    st.session_state.user_chat_partner_name = selected_user[1]
                    st.session_state.user_chat_open = True
                    st.rerun()
            # Chat window
            if st.session_state.get('user_chat_open') and st.session_state.get('user_chat_partner_id'):
                partner_id = st.session_state.user_chat_partner_id
                partner_name = st.session_state.user_chat_partner_name
                st.markdown(f'#### Chat with {partner_name}')
                # Fetch chat history
                conn = mysql.connector.connect(**get_mysql_config())
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT sender_id, message, sent_at FROM user_chats
                    WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                    ORDER BY sent_at ASC
                ''', (st.session_state.user_id, partner_id, partner_id, st.session_state.user_id))
                chat_history = cursor.fetchall()
                cursor.close()
                conn.close()
                # View analysis modal state
                if 'view_analysis_id' not in st.session_state:
                    st.session_state.view_analysis_id = None
                for msg in chat_history:
                    sender = 'You' if msg['sender_id'] == st.session_state.user_id else partner_name
                    # Check if this is a shared analysis message
                    if msg['message'].startswith('📄 [Shared Analysis] Title:') and '||docid:' in msg['message']:
                        title_part, docid_part = msg['message'].split('||docid:')
                        doc_id = int(docid_part.strip())
                        st.markdown(f"**{sender}:** {title_part} <span style='color:#888;font-size:0.8em;'>({msg['sent_at']})</span>", unsafe_allow_html=True)
                        if st.button(f"View Analysis {doc_id}", key=f"view_analysis_{msg['sent_at']}_{doc_id}"):
                            st.session_state.view_analysis_id = doc_id
                    elif msg['message'].startswith('📄 [Shared Data Knowledge]'):
                        # Parse out fields
                        import re
                        content = msg['message']
                        title_match = re.search(r'\*\*Title:\*\* (.*)', content)
                        type_match = re.search(r'\*\*Type:\*\* (.*)', content)
                        source_match = re.search(r'\*\*Source:\*\* (.*)', content)
                        preview_match = re.search(r'\*\*Content Preview:\*\* (.*)\n', content)
                        analysis_match = re.search(r'\*\*AI Analysis:\*\*\n([\s\S]*)', content)
                        title = title_match.group(1).strip() if title_match else 'Untitled'
                        doc_type = type_match.group(1).strip() if type_match else 'unknown'
                        source = source_match.group(1).strip() if source_match else 'unknown'
                        preview = preview_match.group(1).strip() if preview_match else ''
                        analysis = analysis_match.group(1).strip() if analysis_match else ''
                        st.markdown(f"**{sender}:** <b>{title}</b> <span style='color:#888;font-size:0.8em;'>({msg['sent_at']})</span>", unsafe_allow_html=True)
                        st.markdown(f"<div style='margin-left:1em;'><b>Type:</b> {doc_type}<br><b>Source:</b> {source}<br><b>Preview:</b> {preview[:200]}...<br><b>AI Analysis:</b><br>{analysis[:400]}...</div>", unsafe_allow_html=True)
                        # Only show add/download for recipient
                        if msg['receiver_id'] == st.session_state.user_id:
                            colA, colB = st.columns(2)
                            with colA:
                                if st.button(f"Add to My Knowledge Base", key=f"add_kb_{msg['sent_at']}"):
                                    # Insert document for this user
                                    conn = mysql.connector.connect(**get_mysql_config())
                                    cursor = conn.cursor()
                                    metadata = create_legal_document_metadata(title=title, document_type=doc_type, source=source)
                                    embedding = vector_store._generate_embedding(preview)
                                    cursor.execute('''
                                        INSERT INTO documents (user_id, title, document_type, source, content, embedding, metadata)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ''', (st.session_state.user_id, title, doc_type, source, preview, embedding.tobytes(), json.dumps(metadata)))
                                    conn.commit()
                                    cursor.close()
                                    conn.close()
                                    st.success('Added to your knowledge base!')
                            with colB:
                                st.download_button("Download", preview, file_name=f"{title}.txt")
                    else:
                        st.markdown(f"**{sender}:** {msg['message']} <span style='color:#888;font-size:0.8em;'>({msg['sent_at']})</span>", unsafe_allow_html=True)
                # Show analysis modal if requested
                if st.session_state.view_analysis_id:
                    doc_id = st.session_state.view_analysis_id
                    conn = mysql.connector.connect(**get_mysql_config())
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute('SELECT * FROM documents WHERE id = %s', (doc_id,))
                    doc = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if doc:
                        st.markdown('---')
                        st.markdown(f"### 📄 Analysis: {doc['title']}")
                        st.markdown(f"**Type:** {doc['document_type']}  ")
                        st.markdown(f"**Source:** {doc['source']}  ")
                        st.markdown(f"**Created:** {doc['created_at']}  ")
                        st.markdown(f"**Content:**\n\n{doc['content']}")
                        # Download button
                        st.download_button("Download Analysis", doc['content'], file_name=f"analysis_{doc_id}.txt")
                    if st.button("Close Analysis View", key="close_analysis_view"):
                        st.session_state.view_analysis_id = None
                        st.rerun()
                # Message input (fix session_state error)
                chat_input_key = f'user_chat_input_{partner_id}'
                if chat_input_key not in st.session_state:
                    st.session_state[chat_input_key] = ''
                new_msg = st.text_input('Type a message', key=chat_input_key, value=st.session_state[chat_input_key])
                if st.button('Send', key='send_user_chat') and new_msg.strip():
                    conn = mysql.connector.connect(**get_mysql_config())
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO user_chats (sender_id, receiver_id, message) VALUES (%s, %s, %s)
                    ''', (st.session_state.user_id, partner_id, new_msg.strip()))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.session_state[chat_input_key] = ''
                    st.rerun()
                # Share analysis/file by ID, show only AI-generated title and include docid
                st.markdown('---')
                st.markdown('**Share analysis from your knowledge base:**')
                docs = self.list_documents_for_current_user()
                if docs:
                    doc_ids = [d['id'] for d in docs]
                    doc_titles = [f"{d['title']} (ID: {d['id']})" for d in docs]
                    selected_doc_idx = st.selectbox('Select a document to share', list(range(len(doc_titles))), format_func=lambda i: doc_titles[i], key='share_doc_select')
                    if st.button('Share selected analysis', key='share_doc_btn'):
                        doc = docs[selected_doc_idx]
                        # Use AI to generate the title for the analysis
                        try:
                            ai_title_prompt = f"Generate a concise title for this legal analysis: '{doc['content_preview']}'"
                            ai_title = self.llm_engine.generate_response(query=ai_title_prompt)
                        except Exception as e:
                            ai_title = doc['title']
                        share_msg = f"📄 [Shared Analysis] Title: {ai_title.strip()} ||docid:{doc['id']}"
                        conn = mysql.connector.connect(**get_mysql_config())
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_chats (sender_id, receiver_id, message) VALUES (%s, %s, %s)
                        ''', (st.session_state.user_id, partner_id, share_msg))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success('Analysis shared!')
                        st.rerun()
                    # New: Share full content and LLM analysis
                    if st.button('Send Data Knowledge & Analysis', key='share_doc_full_btn'):
                        doc = docs[selected_doc_idx]
                        # Fetch full content from DB
                        conn = mysql.connector.connect(**get_mysql_config())
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute('SELECT * FROM documents WHERE id = %s', (doc['id'],))
                        full_doc = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        if full_doc:
                            # Generate LLM analysis
                            try:
                                analysis = self.llm_engine.analyze_document(full_doc['content'], full_doc['document_type'])
                            except Exception as e:
                                analysis = f"[Error generating analysis: {e}]"
                            msg = f"📄 [Shared Data Knowledge]\n**Title:** {full_doc['title']}\n**Type:** {full_doc['document_type']}\n**Source:** {full_doc['source']}\n**Content Preview:** {full_doc['content'][:800]}...\n\n---\n**AI Analysis:**\n{analysis}"
                            conn = mysql.connector.connect(**get_mysql_config())
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO user_chats (sender_id, receiver_id, message) VALUES (%s, %s, %s)
                            ''', (st.session_state.user_id, partner_id, msg))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success('Data knowledge and analysis shared!')
                            st.rerun()
                if st.button('Close Chat', key='close_user_chat'):
                    st.session_state.user_chat_open = False
                    st.session_state.user_chat_partner_id = None
                    st.session_state.user_chat_partner_name = None
                    st.session_state.view_analysis_id = None
                    st.session_state.show_user_chat = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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
            if st.session_state.get('show_admin_dashboard', False):
                self.render_admin_dashboard()
            elif st.session_state.get('show_settings', False):
                self.render_user_settings()
            elif not self.is_user_logged_in_and_active():
                # Always show login/signup unless user is logged in and active
                self.render_login_signup()
            else:
                # Default: show chat interface
                self.render_chat_interface()
                # Always render user chat widget if logged in and active
                self.render_user_chat_widget()
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {str(e)}")

    def delete_user(self, user_id):
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def update_user_settings(self, user_id, settings):
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET settings = %s WHERE id = %s', (json.dumps(settings), user_id))
        conn.commit()
        cursor.close()
        conn.close()

@app.get("/", include_in_schema=False)
def root(request: Request):
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/documents")
    else:
        return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("login.html", {"request": request, "stats": stats, "active_page": None})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("signup.html", {"request": request, "stats": stats, "active_page": None})

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: dict = Depends(get_current_user)):
    recent_conversations = []  # Replace with real data if available
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "recent_conversations": recent_conversations, "stats": stats, "active_page": "dashboard"}
    )

@app.get("/legal-research", response_class=HTMLResponse)
def legal_research(request: Request, user: dict = Depends(get_current_user)):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("legal_research.html", {"request": request, "user": user, "stats": stats, "active_page": "legal-research"})

@app.get("/document-analysis", response_class=HTMLResponse)
def document_analysis(request: Request, user: dict = Depends(get_current_user)):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("document_analysis.html", {"request": request, "user": user, "stats": stats, "active_page": "document-analysis"})

@app.get("/knowledge-base", response_class=HTMLResponse)
def knowledge_base(request: Request, user: dict = Depends(get_current_user)):
    # Calculate stats for the current user
    user_id = user["id"]
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM documents WHERE user_id = %s", (user_id,))
    total_documents = cursor.fetchone()["total"]
    cursor.execute("SELECT DISTINCT document_type FROM documents WHERE user_id = %s", (user_id,))
    document_types = [row["document_type"] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT source FROM documents WHERE user_id = %s", (user_id,))
    sources = [row["source"] for row in cursor.fetchall()]
    cursor.execute("SELECT id, title, document_type, source, created_at FROM documents WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    documents = cursor.fetchall()
    cursor.close()
    stats = {
        "total_documents": total_documents,
        "document_types": document_types,
        "sources": sources,
        "conversations": 0  # Placeholder, update if you track conversations
    }
    return templates.TemplateResponse("knowledge_base.html", {"request": request, "user": user, "stats": stats, "active_page": "knowledge-base", "documents": documents})

@app.get("/web-research", response_class=HTMLResponse)
def web_research(request: Request, user: dict = Depends(get_current_user)):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("web_research.html", {"request": request, "user": user, "stats": stats, "active_page": "web-research"})

@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request, user: dict = Depends(get_current_user)):
    stats = {"total_documents": 0, "conversations": 0}
    # Load user settings if available
    settings = user.get("settings", {}) if user else {}
    current_provider = settings.get("llm_provider", "ollama")
    current_model = settings.get("llm_model", "llama3:8b")
    return templates.TemplateResponse("settings.html", {"request": request, "user": user, "stats": stats, "active_page": "settings", "current_provider": current_provider, "current_model": current_model})

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    stats = {"total_documents": 0, "conversations": 0}
    user = user_store.get_user_by_username(username)
    if not user or not pwd_context.verify(password, user['password_hash']):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "stats": stats, "active_page": None})
    request.session["user"] = {"id": user["id"], "username": user["username"], "role": user["role"]}
    log_activity(user["id"], "login", {"username": user["username"]})
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/signup", response_class=HTMLResponse)
def signup_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    stats = {"total_documents": 0, "conversations": 0}
    if user_store.get_user_by_username(username):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists.", "stats": stats, "active_page": None})
    password_hash = pwd_context.hash(password)
    user_store.add_user(username, email, password_hash)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
def logout(request: Request):
    user = request.session.get("user")
    if user:
        log_activity(user["id"], "logout", {"username": user["username"]})
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/legal-research", response_class=HTMLResponse)
def legal_research_post(request: Request, user: dict = Depends(get_current_user), query: str = Form(...), jurisdiction: str = Form(...), include_web_search: str = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    error = None
    research_result = None
    kb_results = []
    web_results = []
    try:
        llm_engine = LLMEngine.from_user_settings(user.get('settings'))
        # Try to find a document in the user's KB that matches the query (e.g., 'case law 007.txt')
        doc_context = None
        if query:
            cursor = user_store.conn.cursor(dictionary=True)
            cursor.execute("SELECT title, content FROM documents WHERE user_id = %s", (user["id"],))
            docs = cursor.fetchall()
            cursor.close()
            for doc in docs:
                if doc["title"].lower() in query.lower():
                    doc_context = f"Document: {doc['title']}\n{doc['content'][:2000]}..."  # Limit to 2000 chars
                    break
        # If no direct match, fallback to vector search
        if not doc_context:
            kb_results = vector_store.search(query, n_results=3)
            if kb_results:
                doc_context = "\n\n".join([f"Document: {r['metadata']['title']}\n{r['content'][:1000]}..." for r in kb_results])
        research_result = llm_engine.legal_research(query, jurisdiction) if not doc_context else llm_engine.generate_response(query, context=doc_context)
        # Web research (placeholder)
        if include_web_search:
            web_results = []  # Implement web scraping if needed
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        "legal_research.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "legal-research",
            "query": query,
            "jurisdiction": jurisdiction,
            "include_web_search": include_web_search,
            "research_result": research_result,
            "kb_results": kb_results,
            "web_results": web_results,
            "error": error
        }
    )

@app.post("/document-analysis", response_class=HTMLResponse)
def document_analysis_post(request: Request, user: dict = Depends(get_current_user), document: UploadFile = Form(...), analysis_type: str = Form(...), add_to_kb: str = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    error = None
    analysis_result = None
    kb_success = False
    try:
        # Read and process file
        content = document.file.read()
        filename = document.filename
        # Process document content directly
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(content)
            temp_path = tmp_file.name
        document_text = doc_processor.process_file(temp_path)
        os.remove(temp_path)
        if document_text:
            # Analyze document
            analysis_result = LLMEngine.from_user_settings(user.get('settings')).analyze_document(document_text, analysis_type)
            # Add to KB if requested
            if add_to_kb:
                metadata = create_legal_document_metadata(title=filename, document_type=analysis_type, source="uploaded_document")
                embedding = vector_store._generate_embedding(document_text)
                user_store.add_document(user_id=user["id"], title=filename, document_type=analysis_type, source="uploaded_document", content=document_text, embedding=np.array(embedding, dtype=np.float32), metadata=metadata)
                kb_success = True
                log_activity(user["id"], "document_upload", {"filename": filename, "analysis_type": analysis_type})
        else:
            error = "Could not extract text from document."
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        "document_analysis.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "document-analysis",
            "analysis_result": analysis_result,
            "kb_success": kb_success,
            "error": error
        }
    )

@app.post("/knowledge-base", response_class=HTMLResponse)
def knowledge_base_post(request: Request, user: dict = Depends(get_current_user), search_query: str = Form(...), num_results: int = Form(...), min_score: float = Form(...)):
    stats = {"total_documents": 0, "conversations": 0, "document_types": {}, "sources": {}}
    error = None
    results = []
    try:
        results = vector_store.similarity_search_with_score_threshold(search_query, score_threshold=min_score, max_results=num_results)
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        "knowledge_base.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "knowledge-base",
            "search_query": search_query,
            "num_results": num_results,
            "min_score": min_score,
            "results": results,
            "error": error
        }
    )

@app.post("/web-research", response_class=HTMLResponse)
def web_research_post(request: Request, user: dict = Depends(get_current_user), research_urls: str = Form(...), max_pages: int = Form(...), add_to_kb: str = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    error = None
    all_results = []
    try:
        urls = [url.strip() for url in research_urls.split('\n') if url.strip()]
        for url in urls:
            result = scraper.scrape_url(url)
            if result.success:
                all_results.append({
                    "title": result.title or f"Results from {url}",
                    "url": url,
                    "content": result.content or "No content extracted."
                })
                if add_to_kb:
                    metadata = create_legal_document_metadata(
                        title=result.title or url,
                        document_type="web_research",
                        source=url,
                        date_created=datetime.now().isoformat()
                    )
                    embedding = vector_store._generate_embedding(result.content)
                    user_store.add_document(
                        user_id=user["id"],
                        title=result.title or url,
                        document_type="web_research",
                        source=url,
                        content=result.content,
                        embedding=np.array(embedding, dtype=np.float32),
                        metadata=metadata
                    )
            else:
                all_results.append({
                    "title": f"Failed to scrape {url}",
                    "url": url,
                    "content": result.error or "Unknown error."
                })
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        "web_research.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "web-research",
            "research_urls": research_urls,
            "max_pages": max_pages,
            "add_to_kb": add_to_kb,
            "all_results": all_results,
            "error": error
        }
    )

@app.post("/settings", response_class=HTMLResponse)
def settings_post(request: Request, user: dict = Depends(get_current_user), model_provider: str = Form(None), current_model: str = Form(None), temperature: float = Form(None), max_tokens: int = Form(None), chunk_size: int = Form(None), chunk_overlap: int = Form(None), clear_history: str = Form(None), reset_kb: str = Form(None), export_history: str = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    # Save model provider and model to user settings in MySQL
    settings = user.get("settings", {}) if user else {}
    if model_provider:
        settings["llm_provider"] = model_provider
    if current_model:
        settings["llm_model"] = current_model
    # Save other settings as needed
    # ... (temperature, max_tokens, etc.)
    # Update user in MySQL
    cursor = user_store.conn.cursor()
    cursor.execute("UPDATE users SET settings=%s WHERE id=%s", (json.dumps(settings), user["id"]))
    user_store.conn.commit()
    cursor.close()
    log_activity(user["id"], "settings_change", settings)
    # Update session
    request.session["user"]["settings"] = settings
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "settings",
            "current_provider": settings.get("llm_provider", "ollama"),
            "current_model": settings.get("llm_model", "llama3:8b")
        }
    )

@app.on_event("startup")
def ensure_admin_user():
    admin_username = "admin1"
    admin_password = "1234"
    admin_email = "admin1@example.com"
    admin_user = user_store.get_user_by_username(admin_username)
    if not admin_user:
        password_hash = pwd_context.hash(admin_password)
        user_store.add_user(admin_username, admin_email, password_hash)
        # Set role to admin
        cursor = user_store.conn.cursor()
        cursor.execute("UPDATE users SET role='admin' WHERE username=%s", (admin_username,))
        user_store.conn.commit()
        cursor.close()

@app.get("/api/users/search")
def api_users_search(request: Request, q: str = ""):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    cursor = user_store.conn.cursor(dictionary=True)
    q = q.strip().lower()
    users = []
    if q:
        like_pattern = f"{q}%"
        cursor.execute("SELECT id, username FROM users WHERE id != %s AND LOWER(username) LIKE %s", (user["id"], like_pattern))
        users = cursor.fetchall()
    cursor.close()
    return {"users": users}

@app.post("/api/chat/send")
def api_chat_send(request: Request, message: str = Body(...), receiver_id: int = Body(...)):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    sender_id = user["id"]
    cursor = user_store.conn.cursor()
    cursor.execute(
        "INSERT INTO user_chats (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
        (sender_id, receiver_id, message)
    )
    user_store.conn.commit()
    cursor.close()
    log_activity(sender_id, "chat_send", {"receiver_id": receiver_id, "message": message[:200]})
    return {"success": True}

@app.get("/api/chat/history")
def api_chat_history(request: Request, with_user: int):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    user_id = user["id"]
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT sender_id, receiver_id, message, sent_at FROM user_chats
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY sent_at ASC
        """,
        (user_id, with_user, with_user, user_id)
    )
    messages = cursor.fetchall()
    cursor.close()
    return {"messages": messages}

def log_activity(user_id, event_type, event_data=None):
    try:
        conn = mysql.connector.connect(**get_mysql_config())
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO activity_log (user_id, event_type, event_data) VALUES (%s, %s, %s)',
            (user_id, event_type, json.dumps(event_data) if event_data else None)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

@app.get("/api/knowledge-base/my-documents")
def api_kb_my_documents(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, document_type, source, created_at FROM documents WHERE user_id = %s ORDER BY created_at DESC", (user["id"],))
    docs = cursor.fetchall()
    cursor.close()
    return {"documents": docs}

@app.post("/api/knowledge-base/share")
async def api_kb_share(request: Request):
    data = await request.json()
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    doc_id = data.get("doc_id")
    receiver_id = data.get("receiver_id")
    if not doc_id or not receiver_id:
        return JSONResponse({"error": "Missing doc_id or receiver_id"}, status_code=400)
    # Fetch document
    import mysql.connector
    from utils.config import get_mysql_config
    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
    doc = cursor.fetchone()
    cursor.close()
    if not doc:
        conn.close()
        return JSONResponse({"error": "Document not found"}, status_code=404)
    # Generate LLM analysis
    try:
        analysis = LLMEngine.from_user_settings(user.get('settings')).analyze_document(doc['content'], doc['document_type'])
    except Exception as e:
        analysis = f"[Error generating analysis: {e}]"
    msg = f"📄 [Shared Data Knowledge]\n**Title:** {doc['title']}\n**Type:** {doc['document_type']}\n**Source:** {doc['source']}\n**Content Preview:** {doc['content'][:800]}...\n\n---\n**AI Analysis:**\n{analysis}"
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_chats (sender_id, receiver_id, message) VALUES (%s, %s, %s)
    ''', (user["id"], receiver_id, msg))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}

@app.get("/api/chat/unread_count")
def api_chat_unread_count(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"unread": 0})
    import mysql.connector
    from utils.config import get_mysql_config
    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM user_chats WHERE receiver_id = %s AND is_read = FALSE''', (user["id"],))
    unread = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"unread": unread}

@app.post("/api/chat/mark_read")
def api_chat_mark_read(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"success": False, "error": "Not authenticated"}, status_code=401)
    import mysql.connector
    from utils.config import get_mysql_config
    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor()
    cursor.execute('''UPDATE user_chats SET is_read = TRUE WHERE receiver_id = %s AND is_read = FALSE''', (user["id"],))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}

@app.get("/all-documents", response_class=HTMLResponse)
def all_documents(request: Request, user: dict = Depends(get_current_user)):
    # Only allow logged-in users
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.id, d.title, d.document_type, d.source, d.created_at, u.username as uploader
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        ORDER BY d.created_at DESC
    """)
    documents = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse("all_documents.html", {"request": request, "user": user, "documents": documents})

@app.post("/request-permission", response_class=HTMLResponse)
def request_permission(request: Request, user: dict = Depends(get_current_user), doc_id: int = Form(...)):
    # Get document and uploader
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("SELECT id, uploaded_by FROM documents WHERE id = %s", (doc_id,))
    doc = cursor.fetchone()
    if not doc or not doc["uploaded_by"] or doc["uploaded_by"] == user["id"]:
        cursor.close()
        return RedirectResponse(url="/all-documents", status_code=303)
    # Create permission request
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_permission_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doc_id INT NOT NULL,
            requester_id INT NOT NULL,
            uploader_id INT NOT NULL,
            status VARCHAR(32) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """)
    cursor.execute("""
        INSERT INTO document_permission_requests (doc_id, requester_id, uploader_id, status)
        VALUES (%s, %s, %s, 'pending')
    """, (doc_id, user["id"], doc["uploaded_by"]))
    user_store.conn.commit()
    cursor.close()
    # For now, just show a message (in production, notify uploader)
    return templates.TemplateResponse("permission_requested.html", {"request": request, "user": user})

@app.get("/my-permission-requests", response_class=HTMLResponse)
def my_permission_requests(request: Request, user: dict = Depends(get_current_user)):
    cursor = user_store.conn.cursor(dictionary=True)
    # Outgoing requests
    cursor.execute("""
        SELECT r.id, r.doc_id, d.title, r.status, u.username as uploader
        FROM document_permission_requests r
        JOIN documents d ON r.doc_id = d.id
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE r.requester_id = %s
        ORDER BY r.created_at DESC
    """, (user["id"],))
    outgoing = cursor.fetchall()
    # Incoming requests
    cursor.execute("""
        SELECT r.id, r.doc_id, d.title, r.status, u.username as requester
        FROM document_permission_requests r
        JOIN documents d ON r.doc_id = d.id
        LEFT JOIN users u ON r.requester_id = u.id
        WHERE r.uploader_id = %s
        ORDER BY r.created_at DESC
    """, (user["id"],))
    incoming = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse("my_permission_requests.html", {"request": request, "user": user, "outgoing": outgoing, "incoming": incoming})

@app.post("/permission-request/approve", response_class=HTMLResponse)
def approve_permission_request(request: Request, user: dict = Depends(get_current_user), req_id: int = Form(...)):
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("UPDATE document_permission_requests SET status = 'approved' WHERE id = %s AND uploader_id = %s", (req_id, user["id"]))
    user_store.conn.commit()
    cursor.close()
    return RedirectResponse(url="/my-permission-requests", status_code=303)

@app.post("/permission-request/deny", response_class=HTMLResponse)
def deny_permission_request(request: Request, user: dict = Depends(get_current_user), req_id: int = Form(...)):
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("UPDATE document_permission_requests SET status = 'denied' WHERE id = %s AND uploader_id = %s", (req_id, user["id"]))
    user_store.conn.commit()
    cursor.close()
    return RedirectResponse(url="/my-permission-requests", status_code=303)

if __name__ == "__main__":
    # Initialize and run the application
    app = DALIApp()
    app.run()