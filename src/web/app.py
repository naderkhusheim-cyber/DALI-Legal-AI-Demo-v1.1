"""
DALI Legal AI - Main FastAPI Web Application
ChatGPT-style interface for legal professionals (migrated from Streamlit)
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
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
from utils.document_processor import DocumentProcessor
from utils.config import load_config, get_mysql_config
from scrapers.firecrawl_scraper import FirecrawlScraper

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="src/web/templates")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    user_store = MySQLVectorStore(get_mysql_config())
    MYSQL_AVAILABLE = True
except Exception as e:
    print(f"MySQL not available: {e}")
    user_store = None
    MYSQL_AVAILABLE = False
doc_processor = DocumentProcessor()
vector_store = VectorStore()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_mysql_query(query, params=None, fetch_one=False, fetch_all=False):
    """Safely execute MySQL queries with proper connection handling"""
    if not MYSQL_AVAILABLE or not user_store:
        return None if fetch_one or fetch_all else 0
    
    conn = None
    cursor = None
    try:
        conn = user_store._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"MySQL query error: {e}")
        if conn:
            conn.rollback()
        return None if fetch_one or fetch_all else 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
        'navigation': 'Navigation',
        'dashboard': 'Dashboard',
        'legal_research': 'Legal Research',
        'document_analysis': 'Document Analysis',
        'knowledge_base': 'Knowledge Base',
        'web_research': 'Web Research',
        'settings': 'Settings',
        'welcome_title': '⚖️ Welcome to DALI Legal AI',
        'welcome_subtitle': 'Your intelligent legal assistant is ready to help with:',
        'welcome_bullet1': 'Legal research and analysis',
        'welcome_bullet2': 'Document review and insights',
        'welcome_bullet3': 'Contract analysis',
        'welcome_bullet4': 'Compliance guidance',
        'welcome_hint': 'Start by asking a question or uploading a document using the buttons below.',
        'recent_activity': 'Recent Activity',
        'no_recent_activity': 'No recent activity. Start by asking a legal question or uploading a document.',
        'quick_actions': 'Quick Actions',
        'start_legal_research': 'Start Legal Research',
        'analyze_document': 'Analyze Document',
        'web_research_action': 'Web Research',
        'system_status': 'System Status',
        'system_initialized': 'System Initialized',
        'vector_store_ready': 'Vector Store Ready',
        'web_scraper_ready': 'Web Scraper Ready',
        'quick_stats': 'Quick Stats',
        'documents': 'Documents',
        'conversations': 'Conversations',
        # Login/Signup translations
        'login': 'Login',
        'signup': 'Sign Up',
        'create_account': 'Create Account',
        'join_dali': 'Join DALI Legal AI to access advanced legal research tools.',
        'username': 'Username',
        'password': 'Password',
        'email': 'Email',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'company_name': 'Company Name',
        'job_title': 'Job Title',
        'employee_id': 'Employee ID',
        'phone_number': 'Phone Number',
        'department': 'Department',
        'role': 'Role',
        'user_role': 'User',
        'admin_role': 'Admin',
        'manager_role': 'Manager',
        'lawyer_role': 'Lawyer',
        'paralegal_role': 'Paralegal',
        'dont_have_account': "Don't have an account?",
        'already_have_account': 'Already have an account?',
        'login_here': 'Login here',
        'signup_here': 'Sign up here',
        'hello': 'Hello',
        # Modern Dashboard translations
        'time_saved': 'Time Saved',
        'accuracy': 'Accuracy',
        'type': 'Type',
        'description': 'Description',
        'date': 'Date',
        'status': 'Status',
        'completed': 'Completed',
        'quick_actions_subtitle': 'Common tasks and shortcuts',
        'recent_activity_subtitle': 'Your latest legal research and document analysis',
        'system_status_subtitle': 'Current system health and performance',
        'performance': 'Performance',
        'performance_subtitle': 'Response times and efficiency',
        'response_time': 'Response Time',
        'uptime': 'Uptime',
        'tips': 'Tips & Help',
        'tips_subtitle': 'Get the most out of DALI',
        'tip_1_title': 'Pro Tip:',
        'tip_1_content': 'Use specific legal terms for better search results',
        'tip_2_title': 'New Feature:',
        'tip_2_content': 'Try our enhanced document analysis for contracts',
        'view_help': 'View Help Center',
        # Admin Dashboard translations
        'admin_dashboard': 'Admin Dashboard',
        'admin_panel': 'Administration Panel',
        'user_management': 'User Management',
        'document_management': 'Document Management',
        'analytics': 'Analytics',
        'system_settings': 'System Settings',
        'system_logs': 'System Logs',
        'admin_dashboard_subtitle': 'System overview and management tools',
        'refresh_data': 'Refresh Data',
        'export_report': 'Export Report',
        'total_users': 'Total Users',
        'total_conversations': 'Total Conversations',
        'system_uptime': 'System Uptime',
        'user_activity': 'User Activity',
        'user_activity_subtitle': 'Recent user actions and system usage',
        'user': 'User',
        'action': 'Action',
        'timestamp': 'Timestamp',
        'system_performance': 'System Performance',
        'system_performance_subtitle': 'Real-time system metrics and performance',
        'cpu_usage': 'CPU Usage',
        'memory_usage': 'Memory Usage',
        'disk_usage': 'Disk Usage',
        'network_usage': 'Network Usage',
        'system_status_subtitle': 'All system components status',
        'web_server': 'Web Server',
        'database': 'Database',
        'vector_store': 'Vector Store',
        'ai_engine': 'AI Engine',
        'web_scraper': 'Web Scraper',
        'file_storage': 'File Storage',
        'quick_actions_subtitle': 'Common administrative tasks',
        'manage_users': 'Manage Users',
        'view_logs': 'View System Logs',
        'backup_system': 'Backup System',
        'alerts': 'Alerts & Notifications',
        'alerts_subtitle': 'System alerts and important notifications',
        'alert_1_title': 'Storage Warning:',
        'alert_1_content': 'Disk usage approaching 80%',
        'alert_2_title': 'Update Available:',
        'alert_2_content': 'New system update ready for installation',
        'alert_3_title': 'Backup Complete:',
        'alert_3_content': 'Daily backup completed successfully',
        # ChatGPT-style UI translations
        'new_chat': 'New Chat',
        'legal_tools': 'Legal Tools',
        'account': 'Account',
        'role_admin': 'Administrator',
        'role_user': 'User',
        'role_manager': 'Manager',
        'role_lawyer': 'Lawyer',
        'role_paralegal': 'Paralegal',
        'welcome_title': 'Welcome to DALI Legal AI',
        'welcome_description': 'Your intelligent legal assistant is ready to help with research, document analysis, and legal insights.',
        'type_message': 'Type your legal question here...',
        'overview': 'Overview',
        'management': 'Management',
        'system': 'System',
        'system_overview': 'System Overview',
        'system_overview_subtitle': 'Key metrics and system health',
        'new_users_week': 'New Users This Week',
        # Additional ChatGPT UI translations
        'new_research': 'New Research',
        'new_analysis': 'New Analysis',
        'new_search': 'New Search',
        'new_settings': 'New Settings',
        'legal_research_subtitle': 'Ask questions about Saudi Arabian law and get intelligent answers',
        'legal_research_description': 'Ask questions about Saudi Arabian law, regulations, and legal precedents. Get intelligent answers based on our comprehensive legal database.',
        'business_law': 'Business Law',
        'labor_law': 'Labor Law',
        'tax_law': 'Tax Law',
        'ip_law': 'Intellectual Property',
        'ask_legal_question': 'Ask your legal question here...',
        'document_analysis_subtitle': 'Upload and analyze legal documents with AI-powered insights',
        'document_analysis_description': 'Upload legal documents, contracts, or agreements and get AI-powered analysis, summaries, and insights.',
        'upload_document': 'Upload Document',
        'analyze_contract': 'Analyze Contract',
        'summarize_document': 'Summarize Document',
        'extract_clauses': 'Extract Clauses',
        'upload_subtitle': 'Select a legal document to analyze',
        'select_file': 'Select File',
        'analysis_type': 'Analysis Type',
        'summary': 'Summary',
        'contract_analysis': 'Contract Analysis',
        'compliance_check': 'Compliance Check',
        'document_title': 'Document Title',
        'enter_title': 'Enter document title...',
        'upload_and_analyze': 'Upload & Analyze',
        'ask_about_document': 'Ask questions about your document...',
        'knowledge_base_subtitle': 'Search and manage your legal documents and knowledge',
        'knowledge_base_description': 'Search through your uploaded documents, legal precedents, and knowledge base. Find relevant information quickly and efficiently.',
        'search_documents': 'Search Documents',
        'view_all_documents': 'View All Documents',
        'manage_categories': 'Manage Categories',
        'search_knowledge_base': 'Search Knowledge Base',
        'search_subtitle': 'Find relevant documents and information',
        'search_query': 'Search Query',
        'enter_search_terms': 'Enter search terms...',
        'number_of_results': 'Number of Results',
        'minimum_score': 'Minimum Score',
        'search': 'Search',
        'document_management': 'Document Management',
        'manage_your_documents': 'Manage your uploaded documents',
        'ask_about_knowledge': 'Ask questions about your knowledge base...',
        'web_research_subtitle': 'Scrape and analyze web content for legal research',
        'web_research_description': 'Scrape websites, extract legal information, and add content to your knowledge base for comprehensive legal research.',
        'scrape_website': 'Scrape Website',
        'research_legal_sites': 'Research Legal Sites',
        'extract_content': 'Extract Content',
        'add_to_knowledge_base': 'Add to Knowledge Base',
        'enter_url_to_research': 'Enter a URL to research and scrape content',
        'website_url': 'Website URL',
        'research_type': 'Research Type',
        'scrape_content': 'Scrape Content',
        'analyze_content': 'Analyze Content',
        'extract_key_points': 'Extract Key Points',
        'summarize_content': 'Summarize Content',
        'start_research': 'Start Research',
        'ask_about_web_research': 'Ask questions about web research or enter URLs...',
        'settings_subtitle': 'Manage your account preferences and system settings',
        'user_profile': 'User Profile',
        'manage_your_profile': 'Manage your personal information and preferences',
        'edit_profile': 'Edit Profile',
        'system_preferences': 'System Preferences',
        'customize_your_experience': 'Customize your experience with DALI Legal AI',
        'language_description': 'Choose your preferred language',
        'theme': 'Theme',
        'theme_description': 'Choose your preferred theme',
        'notifications': 'Notifications',
        'notifications_description': 'Manage notification preferences',
        'enabled': 'Enabled',
        'security_settings': 'Security Settings',
        'manage_your_security': 'Manage your account security and privacy',
        'change_password': 'Change Password',
        'two_factor_auth': 'Two-Factor Authentication',
        'session_management': 'Session Management',
        'privacy_settings': 'Privacy Settings',
        'data_management': 'Data Management',
        'manage_your_data': 'Manage your documents and data',
        'export_data': 'Export Data',
        'delete_account': 'Delete Account',
        'data_privacy': 'Data Privacy',
        # Settings functionality translations
        'system_configuration': 'System Configuration',
        'configure_llm_settings': 'Configure LLM and system settings',
        'model_provider': 'Model Provider',
        'current_model': 'Current Model',
        'response_temperature': 'Response Temperature',
        'max_response_tokens': 'Max Response Tokens',
        'update_llm_settings': 'Update LLM Settings',
        'vector_store_settings': 'Vector Store Settings',
        'configure_document_processing': 'Configure document processing settings',
        'document_chunk_size': 'Document Chunk Size',
        'chunk_overlap': 'Chunk Overlap',
        'update_vector_store_settings': 'Update Vector Store Settings',
        'clear_conversation_history': 'Clear Conversation History',
        'reset_knowledge_base': 'Reset Knowledge Base',
        'export_conversation_history': 'Export Conversation History',
        # New settings tab translations
        'manage_your_preferences': 'Manage your account preferences and system settings',
        'llm_settings': 'LLM Settings',
        'customize_your_experience': 'Customize your experience and interface preferences',
        'toggle_theme': 'Toggle Theme',
        'toggle_language': 'Toggle Language',
        'notification_settings': 'Notification Settings',
        # Login page translations
        'welcome_back': 'Welcome Back',
        'login_subtitle': 'Sign in to your DALI Legal AI account',
        'language': 'Language',
        'select_your_preferred_language': 'Select your preferred language',
        'enter_your_credentials': 'Enter your username and password to access your account',
        'enter_username': 'Enter your username',
        'enter_password': 'Enter your password',
        'new_user': 'New User?',
        'create_account_subtitle': 'Create a new account to get started',
        'what_you_get': 'What You Get',
        'powerful_legal_ai_features': 'Access powerful legal AI features',
        'research_description': 'AI-powered legal research and analysis',
        'analysis_description': 'Upload and analyze legal documents',
        'web_description': 'Scrape and analyze web content',
        'kb_description': 'Build your personal legal knowledge base',
        'please_fill_all_fields': 'Please fill in all fields',
        'logging_in': 'Logging in...',
        # Modern login page translations
        'welcome_to_dali': 'Welcome to DALI Legal AI',
        'legal_updates': 'Legal Updates',
        'modification_date': 'Modification Date:',
        'effective_in_18_days': 'Effective in 18 days: 21 hours: 03 minutes',
        'amendment_link': 'Amendment Link:',
        'royal_decree_m44': 'Royal Decree No. (M/44) for 1446',
        'amendment_description': 'Adding two definitions to the article, with the following text: Assignment: a service providing a worker to work for a non-employer through a licensed establishment for this purpose.',
        'copy_update': 'Copy Update',
        'countdown_feature': 'Upcoming Updates Countdown Feature',
        'countdown_description': 'You can see upcoming system updates before they take effect, with a countdown to the effective date, to be prepared in advance and stay informed.',
        'view_all_updates': 'View All Updates',
        'legal_ai': 'Legal AI',
        'request_free_trial': 'Request Free Trial',
        'enter_username': 'Enter your username',
        'remember_me': 'Remember me',
        'remember_description': 'When approved, enjoy longer and more comfortable login on the same browser.',
        'forgot_password': 'Forgot password?',
        'copied': 'Copied!',
        # Knowledge Base Management translations
        'knowledge_base_management': 'Knowledge Base Management',
        'manage_your_documents': 'View and manage your uploaded documents',
        'file_name': 'File Name',
        'file_type': 'Type',
        'upload_date': 'Upload Date',
        'file_size': 'Size',
        'refresh': 'Refresh',
        'export_kb': 'Export Knowledge Base',
        # Admin User Management translations
        'user_management': 'User Management',
        'manage_all_users': 'Manage all users, roles, and permissions',
        'user_statistics': 'User Statistics',
        'overview_of_user_data': 'Overview of user data and activity',
        'total_users': 'Total Users',
        'active_users': 'Active Users',
        'admin_users': 'Admin Users',
        'all_users': 'All Users',
        'manage_user_accounts': 'Manage user accounts, roles, and permissions',
        'export_users': 'Export Users',
        'bulk_actions': 'Bulk Actions',
        'username': 'Username',
        'email': 'Email',
        'role': 'Role',
        'status': 'Status',
        'last_active': 'Last Active',
        'created_at': 'Created',
        # Profile Management translations
        'manage_your_profile': 'Manage your personal information and preferences',
        'username_cannot_change': 'Username cannot be changed',
        'email_cannot_change': 'Email cannot be changed',
        'save_changes': 'Save Changes',
        'reset': 'Reset',
        'saving': 'Saving...',
        'profile_updated_successfully': 'Profile updated successfully!',
        'error_updating_profile': 'Error updating profile',
        'confirm_reset_profile': 'Are you sure you want to reset all changes?',
        # Password Change translations
        'current_password': 'Current Password',
        'new_password': 'New Password',
        'confirm_password': 'Confirm New Password',
        'password_min_length': 'Password must be at least 6 characters long',
        'cancel': 'Cancel',
        'passwords_do_not_match': 'New passwords do not match',
        'password_too_short': 'Password must be at least 6 characters long',
        'changing_password': 'Changing Password...',
        'password_changed_successfully': 'Password changed successfully!',
        'error_changing_password': 'Error changing password',
        # Document Analysis translations
        'download_pdf': 'Download PDF',
        'share_analysis': 'Share Analysis',
        'add_to_kb': 'Add to Knowledge Base',
        'no_analysis_to_download': 'No analysis available to download',
        'enter_username_to_share': 'Enter username to share analysis with:',
        'no_analysis_to_share': 'No analysis available to share',
        'analysis_shared_successfully': 'Analysis shared successfully!',
        'error_sharing_analysis': 'Error sharing analysis',
        'no_analysis_to_add': 'No analysis available to add to knowledge base',
        'analysis_added_to_kb': 'Analysis added to knowledge base successfully!',
        'error_adding_to_kb': 'Error adding to knowledge base',
        # Voice-to-Text translations
        'voice_input': 'Voice Input',
        'listening': 'Listening...',
        'voice_recognition_error': 'Voice recognition error. Please try again.',
        'voice_not_supported': 'Voice recognition is not supported in this browser.',
        'error_starting_voice': 'Error starting voice recognition. Please try again.',
        # Document sharing translations
        'share_document': 'Share Document',
        'select_user': 'Select User to Share With',
        'loading_users': 'Loading users...',
        'error_loading_users': 'Error loading users',
        'please_select_user': 'Please select a user to share with',
        'no_document_selected': 'No document selected',
        'document_shared_successfully': 'Document shared successfully!',
        'error_sharing_document': 'Error sharing document',
        'share': 'Share',
        # Document view translations
        'document_viewer': 'Document Viewer',
        'document_type': 'Type',
        'source': 'Source',
        'created': 'Created',
        'download': 'Download',
        'edit': 'Edit',
        'edit_functionality_coming_soon': 'Edit functionality coming soon!',
        # AI Analysis translations
        'ai_analysis': 'AI Analysis',
        'analysis_for_query': 'Analysis for',
        # Dashboard translations
        'what_to_search_today': 'What do you want to search for today?',
        'all_results': 'All Results',
        'search_here': 'Search here...',
        'systems_regulations': 'Systems / Regulations',
        'judicial_precedents': 'Judicial Precedents',
        'orders_directives': 'Orders / Directives',
        'books_sources': 'Books / Sources',
        'supporting_forms': 'Supporting Forms',
        'saudi_law_updates': 'Saudi Law Updates',
        'show_more': 'Show More',
        'update_1': 'Latest Legal Update',
        'update_2': 'Regulation Changes',
        'update_3': 'Court Decisions',
        'search_legal_documents': 'Search legal documents and precedents',
        'analyze_contracts_documents': 'Analyze contracts and documents',
        'manage_your_documents': 'Manage your documents',
        'scrape_legal_websites': 'Scrape legal websites',
        # Navigation translations
        'back': 'Back',
        # Signup page translations
        'join_dali_family': 'Join the DALI Family',
        'legal_research_description': 'Access AI-powered legal research tools with comprehensive database of Saudi legal documents, regulations, and case law.',
        'document_analysis_description': 'Upload and analyze legal documents with AI-powered insights, contract review, and compliance checking.',
        'why_choose_dali': 'Why Choose DALI?',
        'why_choose_description': 'DALI Legal AI provides comprehensive legal research tools specifically designed for Saudi Arabian law, helping legal professionals work more efficiently and accurately.',
        'learn_more': 'Learn More',
        'already_have_account': 'Already have account?',
        'enter_first_name': 'Enter your first name',
        'enter_last_name': 'Enter your last name',
        'enter_company_name': 'Enter your company name',
        'enter_job_title': 'Enter your job title',
        'enter_employee_id': 'Enter employee ID (optional)',
        'enter_phone': 'Enter phone number (optional)',
        'enter_department': 'Enter your department (optional)',
        'user': 'User',
        'admin': 'Admin',
        'login_here': 'Login here',
        'please_fill_required_fields': 'Please fill in all required fields',
        'creating_account': 'Creating account...',
        'research_result': 'Research Result',
        'query': 'Query',
        'recent_research': 'Recent Research',
        'new_research': 'New Research',
        'analysis_result': 'Analysis Result',
        'document': 'Document',
        'search_results': 'Search Results'
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
        'navigation': 'التنقل',
        'dashboard': 'لوحة التحكم',
        'legal_research': 'البحث القانوني',
        'document_analysis': 'تحليل المستندات',
        'knowledge_base': 'قاعدة المعرفة',
        'web_research': 'البحث على الويب',
        'settings': 'الإعدادات',
        'welcome_title': '⚖️ مرحبًا بك في دالي للذكاء الاصطناعي القانوني',
        'welcome_subtitle': 'مساعدك القانوني الذكي جاهز لمساعدتك في:',
        'welcome_bullet1': 'البحث والتحليل القانوني',
        'welcome_bullet2': 'مراجعة المستندات وتقديم الرؤى',
        'welcome_bullet3': 'تحليل العقود',
        'welcome_bullet4': 'إرشادات الامتثال',
        'welcome_hint': 'ابدأ بطرح سؤال أو تحميل مستند باستخدام الأزرار أدناه.',
        'recent_activity': 'النشاط الأخير',
        'no_recent_activity': 'لا يوجد نشاط حديث. ابدأ بطرح سؤال قانوني أو تحميل مستند.',
        'quick_actions': 'الإجراءات السريعة',
        'start_legal_research': 'بدء البحث القانوني',
        'analyze_document': 'تحليل المستند',
        'web_research_action': 'البحث على الويب',
        'system_status': 'حالة النظام',
        'system_initialized': 'تم تهيئة النظام',
        'vector_store_ready': 'قاعدة البيانات المتجهة جاهزة',
        'web_scraper_ready': 'أداة استخراج الويب جاهزة',
        'quick_stats': 'الإحصائيات السريعة',
        'documents': 'المستندات',
        'conversations': 'المحادثات',
        # Login/Signup translations
        'login': 'تسجيل الدخول',
        'signup': 'إنشاء حساب',
        'create_account': 'إنشاء حساب',
        'join_dali': 'انضم إلى DALI Legal AI للوصول إلى أدوات البحث القانوني المتقدمة.',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'email': 'البريد الإلكتروني',
        'first_name': 'الاسم الأول',
        'last_name': 'اسم العائلة',
        'company_name': 'اسم الشركة',
        'job_title': 'المسمى الوظيفي',
        'employee_id': 'رقم الموظف',
        'phone_number': 'رقم الهاتف',
        'department': 'القسم',
        'role': 'الدور',
        'user_role': 'مستخدم',
        'admin_role': 'مدير',
        'manager_role': 'مدير',
        'lawyer_role': 'محامي',
        'paralegal_role': 'مساعد قانوني',
        'dont_have_account': 'ليس لديك حساب؟',
        'already_have_account': 'لديك حساب بالفعل؟',
        'login_here': 'سجل الدخول هنا',
        'signup_here': 'أنشئ حساب هنا',
        'hello': 'مرحباً',
        # Modern Dashboard translations
        'time_saved': 'الوقت المحفوظ',
        'accuracy': 'الدقة',
        'type': 'النوع',
        'description': 'الوصف',
        'date': 'التاريخ',
        'status': 'الحالة',
        'completed': 'مكتمل',
        'quick_actions_subtitle': 'المهام الشائعة والاختصارات',
        'recent_activity_subtitle': 'أحدث أبحاثك القانونية وتحليل المستندات',
        'system_status_subtitle': 'صحة النظام والأداء الحالي',
        'performance': 'الأداء',
        'performance_subtitle': 'أوقات الاستجابة والكفاءة',
        'response_time': 'وقت الاستجابة',
        'uptime': 'وقت التشغيل',
        'tips': 'النصائح والمساعدة',
        'tips_subtitle': 'احصل على أقصى استفادة من DALI',
        'tip_1_title': 'نصيحة احترافية:',
        'tip_1_content': 'استخدم المصطلحات القانونية المحددة للحصول على نتائج بحث أفضل',
        'tip_2_title': 'ميزة جديدة:',
        'tip_2_content': 'جرب تحليل المستندات المحسن للعقود',
        'view_help': 'عرض مركز المساعدة',
        # Admin Dashboard translations
        'admin_dashboard': 'لوحة تحكم المدير',
        'admin_panel': 'لوحة الإدارة',
        'user_management': 'إدارة المستخدمين',
        'document_management': 'إدارة المستندات',
        'analytics': 'التحليلات',
        'system_settings': 'إعدادات النظام',
        'system_logs': 'سجلات النظام',
        'admin_dashboard_subtitle': 'نظرة عامة على النظام وأدوات الإدارة',
        'refresh_data': 'تحديث البيانات',
        'export_report': 'تصدير التقرير',
        'total_users': 'إجمالي المستخدمين',
        'total_conversations': 'إجمالي المحادثات',
        'system_uptime': 'وقت تشغيل النظام',
        'user_activity': 'نشاط المستخدمين',
        'user_activity_subtitle': 'أحدث إجراءات المستخدمين واستخدام النظام',
        'user': 'المستخدم',
        'action': 'الإجراء',
        'timestamp': 'الطابع الزمني',
        'system_performance': 'أداء النظام',
        'system_performance_subtitle': 'مقاييس النظام في الوقت الفعلي والأداء',
        'cpu_usage': 'استخدام المعالج',
        'memory_usage': 'استخدام الذاكرة',
        'disk_usage': 'استخدام القرص',
        'network_usage': 'استخدام الشبكة',
        'system_status_subtitle': 'حالة جميع مكونات النظام',
        'web_server': 'خادم الويب',
        'database': 'قاعدة البيانات',
        'vector_store': 'مخزن المتجهات',
        'ai_engine': 'محرك الذكاء الاصطناعي',
        'web_scraper': 'أداة استخراج الويب',
        'file_storage': 'تخزين الملفات',
        'quick_actions_subtitle': 'المهام الإدارية الشائعة',
        'manage_users': 'إدارة المستخدمين',
        'view_logs': 'عرض سجلات النظام',
        'backup_system': 'نسخ احتياطي للنظام',
        'alerts': 'التنبيهات والإشعارات',
        'alerts_subtitle': 'تنبيهات النظام والإشعارات المهمة',
        'alert_1_title': 'تحذير التخزين:',
        'alert_1_content': 'استخدام القرص يقترب من 80%',
        'alert_2_title': 'تحديث متاح:',
        'alert_2_content': 'تحديث نظام جديد جاهز للتثبيت',
        'alert_3_title': 'اكتمل النسخ الاحتياطي:',
        'alert_3_content': 'اكتمل النسخ الاحتياطي اليومي بنجاح',
        # ChatGPT-style UI translations
        'new_chat': 'محادثة جديدة',
        'legal_tools': 'الأدوات القانونية',
        'account': 'الحساب',
        'role_admin': 'مدير',
        'role_user': 'مستخدم',
        'role_manager': 'مدير',
        'role_lawyer': 'محامي',
        'role_paralegal': 'مساعد قانوني',
        'welcome_title': 'مرحباً بك في DALI Legal AI',
        'welcome_description': 'مساعدك القانوني الذكي جاهز لمساعدتك في البحث وتحليل المستندات والرؤى القانونية.',
        'type_message': 'اكتب سؤالك القانوني هنا...',
        'overview': 'نظرة عامة',
        'management': 'الإدارة',
        'system': 'النظام',
        'system_overview': 'نظرة عامة على النظام',
        'system_overview_subtitle': 'المقاييس الرئيسية وصحة النظام',
        'new_users_week': 'مستخدمين جدد هذا الأسبوع',
        # Settings functionality translations
        'system_configuration': 'إعدادات النظام',
        'configure_llm_settings': 'تكوين إعدادات LLM والنظام',
        'model_provider': 'مزود النموذج',
        'current_model': 'النموذج الحالي',
        'response_temperature': 'درجة حرارة الاستجابة',
        'max_response_tokens': 'الحد الأقصى لرموز الاستجابة',
        'update_llm_settings': 'تحديث إعدادات LLM',
        'vector_store_settings': 'إعدادات مخزن المتجهات',
        'configure_document_processing': 'تكوين إعدادات معالجة المستندات',
        'document_chunk_size': 'حجم قطع المستندات',
        'chunk_overlap': 'تداخل القطع',
        'update_vector_store_settings': 'تحديث إعدادات مخزن المتجهات',
        'clear_conversation_history': 'مسح تاريخ المحادثات',
        'reset_knowledge_base': 'إعادة تعيين قاعدة المعرفة',
        'export_conversation_history': 'تصدير تاريخ المحادثات',
        # New settings tab translations
        'manage_your_preferences': 'إدارة تفضيلات حسابك وإعدادات النظام',
        'llm_settings': 'إعدادات LLM',
        'customize_your_experience': 'تخصيص تجربتك وتفضيلات الواجهة',
        'toggle_theme': 'تبديل المظهر',
        'toggle_language': 'تبديل اللغة',
        'notification_settings': 'إعدادات الإشعارات',
        # Login page translations
        'welcome_back': 'مرحباً بعودتك',
        'login_subtitle': 'سجل الدخول إلى حسابك في دالي للذكاء الاصطناعي القانوني',
        'language': 'اللغة',
        'select_your_preferred_language': 'اختر لغتك المفضلة',
        'enter_your_credentials': 'أدخل اسم المستخدم وكلمة المرور للوصول إلى حسابك',
        'enter_username': 'أدخل اسم المستخدم',
        'enter_password': 'أدخل كلمة المرور',
        'new_user': 'مستخدم جديد؟',
        'create_account_subtitle': 'أنشئ حساباً جديداً للبدء',
        'what_you_get': 'ما ستحصل عليه',
        'powerful_legal_ai_features': 'الوصول إلى ميزات الذكاء الاصطناعي القانوني القوية',
        'research_description': 'البحث والتحليل القانوني بالذكاء الاصطناعي',
        'analysis_description': 'رفع وتحليل المستندات القانونية',
        'web_description': 'استخراج وتحليل محتوى الويب',
        'kb_description': 'بناء قاعدة المعرفة القانونية الشخصية',
        'please_fill_all_fields': 'يرجى ملء جميع الحقول',
        'logging_in': 'جاري تسجيل الدخول...',
        # Modern login page translations
        'welcome_to_dali': 'مرحباً بك في دالي للذكاء الاصطناعي القانوني',
        'legal_updates': 'التحديثات القانونية',
        'modification_date': 'تاريخ التعديل:',
        'effective_in_18_days': 'يسري التعديل بعد 18 يوم: 21 ساعة: 03 دقائق',
        'amendment_link': 'رابط التعديل:',
        'royal_decree_m44': 'المرسوم الملكي رقم (م/44) لعام 1446',
        'amendment_description': 'إضافة تعريفين للمادة، بالنص التالي: الإسناد: خدمة توفير عامل للعمل لدى غير صاحب العمل وذلك من خلال منشأة مرخص لها لهذا الغرض.',
        'copy_update': 'نسخ التحديث',
        'countdown_feature': 'ميزة العد التنازلي للتحديثات القادمة',
        'countdown_description': 'يمكنك رؤية التحديثات القادمة للنظام قبل سريانها، مع وجود عداد تنازلي لموعد السريان، لتكون على استعداد مسبق، واطلاع دائم',
        'view_all_updates': 'عرض كل التحديثات',
        'legal_ai': 'الذكاء الاصطناعي القانوني',
        'request_free_trial': 'طلب تجربة المنصة مجاناً',
        'enter_username': 'أدخل اسم المستخدم',
        'remember_me': 'تذكرني',
        'remember_description': 'عند الموافقة استمتع بتسجيل دخول أطول وأكثر راحة على نفس المتصفح.',
        'forgot_password': 'هل نسيت كلمة المرور؟',
        'copied': 'تم النسخ!',
        # Knowledge Base Management translations
        'knowledge_base_management': 'إدارة قاعدة المعرفة',
        'manage_your_documents': 'عرض وإدارة المستندات المرفوعة',
        'file_name': 'اسم الملف',
        'file_type': 'النوع',
        'upload_date': 'تاريخ الرفع',
        'file_size': 'الحجم',
        'refresh': 'تحديث',
        'export_kb': 'تصدير قاعدة المعرفة',
        # Admin User Management translations
        'user_management': 'إدارة المستخدمين',
        'manage_all_users': 'إدارة جميع المستخدمين والأدوار والصلاحيات',
        'user_statistics': 'إحصائيات المستخدمين',
        'overview_of_user_data': 'نظرة عامة على بيانات المستخدمين والنشاط',
        'total_users': 'إجمالي المستخدمين',
        'active_users': 'المستخدمون النشطون',
        'admin_users': 'مستخدمو الإدارة',
        'all_users': 'جميع المستخدمين',
        'manage_user_accounts': 'إدارة حسابات المستخدمين والأدوار والصلاحيات',
        'export_users': 'تصدير المستخدمين',
        'bulk_actions': 'إجراءات مجمعة',
        'username': 'اسم المستخدم',
        'email': 'البريد الإلكتروني',
        'role': 'الدور',
        'status': 'الحالة',
        'last_active': 'آخر نشاط',
        'created_at': 'تاريخ الإنشاء',
        # Profile Management translations
        'manage_your_profile': 'إدارة معلوماتك الشخصية والتفضيلات',
        'username_cannot_change': 'لا يمكن تغيير اسم المستخدم',
        'email_cannot_change': 'لا يمكن تغيير البريد الإلكتروني',
        'save_changes': 'حفظ التغييرات',
        'reset': 'إعادة تعيين',
        'saving': 'جاري الحفظ...',
        'profile_updated_successfully': 'تم تحديث الملف الشخصي بنجاح!',
        'error_updating_profile': 'خطأ في تحديث الملف الشخصي',
        'confirm_reset_profile': 'هل أنت متأكد من أنك تريد إعادة تعيين جميع التغييرات؟',
        # Password Change translations
        'current_password': 'كلمة المرور الحالية',
        'new_password': 'كلمة المرور الجديدة',
        'confirm_password': 'تأكيد كلمة المرور الجديدة',
        'password_min_length': 'يجب أن تكون كلمة المرور 6 أحرف على الأقل',
        'cancel': 'إلغاء',
        'passwords_do_not_match': 'كلمات المرور الجديدة غير متطابقة',
        'password_too_short': 'يجب أن تكون كلمة المرور 6 أحرف على الأقل',
        'changing_password': 'جاري تغيير كلمة المرور...',
        'password_changed_successfully': 'تم تغيير كلمة المرور بنجاح!',
        'error_changing_password': 'خطأ في تغيير كلمة المرور',
        # Document Analysis translations
        'download_pdf': 'تحميل PDF',
        'share_analysis': 'مشاركة التحليل',
        'add_to_kb': 'إضافة إلى قاعدة المعرفة',
        'no_analysis_to_download': 'لا يوجد تحليل متاح للتحميل',
        'enter_username_to_share': 'أدخل اسم المستخدم لمشاركة التحليل معه:',
        'no_analysis_to_share': 'لا يوجد تحليل متاح للمشاركة',
        'analysis_shared_successfully': 'تم مشاركة التحليل بنجاح!',
        'error_sharing_analysis': 'خطأ في مشاركة التحليل',
        'no_analysis_to_add': 'لا يوجد تحليل متاح لإضافته إلى قاعدة المعرفة',
        'analysis_added_to_kb': 'تم إضافة التحليل إلى قاعدة المعرفة بنجاح!',
        'error_adding_to_kb': 'خطأ في إضافة إلى قاعدة المعرفة',
        # Voice-to-Text translations
        'voice_input': 'إدخال صوتي',
        'listening': 'جاري الاستماع...',
        'voice_recognition_error': 'خطأ في التعرف على الصوت. يرجى المحاولة مرة أخرى.',
        'voice_not_supported': 'التعرف على الصوت غير مدعوم في هذا المتصفح.',
        'error_starting_voice': 'خطأ في بدء التعرف على الصوت. يرجى المحاولة مرة أخرى.',
        # Document sharing translations
        'share_document': 'مشاركة المستند',
        'select_user': 'اختر المستخدم للمشاركة معه',
        'loading_users': 'جاري تحميل المستخدمين...',
        'error_loading_users': 'خطأ في تحميل المستخدمين',
        'please_select_user': 'يرجى اختيار مستخدم للمشاركة معه',
        'no_document_selected': 'لم يتم اختيار مستند',
        'document_shared_successfully': 'تم مشاركة المستند بنجاح!',
        'error_sharing_document': 'خطأ في مشاركة المستند',
        'share': 'مشاركة',
        # Document view translations
        'document_viewer': 'عارض المستندات',
        'document_type': 'النوع',
        'source': 'المصدر',
        'created': 'تاريخ الإنشاء',
        'download': 'تحميل',
        'edit': 'تعديل',
        'edit_functionality_coming_soon': 'وظيفة التعديل قريباً!',
        # AI Analysis translations
        'ai_analysis': 'التحليل بالذكاء الاصطناعي',
        'analysis_for_query': 'التحليل لـ',
        # Dashboard translations
        'what_to_search_today': 'ما الذي تود البحث عنه اليوم؟',
        'all_results': 'جميع النتائج',
        'search_here': 'ابحث هنا...',
        'systems_regulations': 'أنظمة / لوائح',
        'judicial_precedents': 'سوابق قضائية',
        'orders_directives': 'أوامر / تعاميم',
        'books_sources': 'كتب / مصادر ثانوية',
        'supporting_forms': 'نماذج مساندة',
        'saudi_law_updates': 'تحديثات القانون السعودي',
        'show_more': 'عرض المزيد',
        'update_1': 'أحدث التحديثات القانونية',
        'update_2': 'تغييرات اللوائح',
        'update_3': 'قرارات المحاكم',
        'search_legal_documents': 'البحث في المستندات القانونية والسوابق',
        'analyze_contracts_documents': 'تحليل العقود والمستندات',
        'manage_your_documents': 'إدارة مستنداتك',
        'scrape_legal_websites': 'استخراج البيانات من المواقع القانونية',
        # Navigation translations
        'back': 'رجوع',
        # Signup page translations
        'join_dali_family': 'انضم إلى عائلة دالي',
        'legal_research_description': 'الوصول إلى أدوات البحث القانوني بالذكاء الاصطناعي مع قاعدة بيانات شاملة للمستندات القانونية السعودية واللوائح والسوابق القضائية.',
        'document_analysis_description': 'رفع وتحليل المستندات القانونية مع رؤى مدعومة بالذكاء الاصطناعي ومراجعة العقود والتحقق من الامتثال.',
        'why_choose_dali': 'لماذا تختار دالي؟',
        'why_choose_description': 'دالي للذكاء الاصطناعي القانوني يوفر أدوات بحث قانوني شاملة مصممة خصيصاً للقانون السعودي، مما يساعد المهنيين القانونيين على العمل بكفاءة ودقة أكبر.',
        'learn_more': 'اعرف المزيد',
        'already_have_account': 'لديك حساب بالفعل؟',
        'enter_first_name': 'أدخل اسمك الأول',
        'enter_last_name': 'أدخل اسمك الأخير',
        'enter_company_name': 'أدخل اسم الشركة',
        'enter_job_title': 'أدخل المسمى الوظيفي',
        'enter_employee_id': 'أدخل رقم الموظف (اختياري)',
        'enter_phone': 'أدخل رقم الهاتف (اختياري)',
        'enter_department': 'أدخل القسم (اختياري)',
        'user': 'مستخدم',
        'admin': 'مدير',
        'login_here': 'سجل الدخول هنا',
        'please_fill_required_fields': 'يرجى ملء جميع الحقول المطلوبة',
        'creating_account': 'جاري إنشاء الحساب...',
        'research_result': 'نتيجة البحث',
        'query': 'الاستعلام',
        'recent_research': 'البحث الأخير',
        'new_research': 'بحث جديد',
        'analysis_result': 'نتيجة التحليل',
        'document': 'المستند',
        'search_results': 'نتائج البحث'
    }
}
def t(key, request=None):
    """Translation function that uses session language"""
    if request and hasattr(request, 'session'):
        lang = request.session.get("language", "en")
    else:
        lang = "en"  # Default to English
    return LANGUAGES[lang].get(key, key)


# Remove the entire UserDatabase class and all references to it, including instantiation and method calls.


class DALIApp:
    """Main DALI Legal AI Application with ChatGPT-like interface"""
    
    def __init__(self):
        self.config = load_config("config/config.yaml")
        print(f"Loaded config: {self.config}")  # DEBUG
        print(f"Firecrawl API key from config: {self.config.get('firecrawl', {}).get('api_key')}")  # DEBUG
        self.initialize_components()
    
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
            firecrawl_api_key = self.config.get('firecrawl', {}).get('api_key')
            self.scraper = FirecrawlScraper(
                api_key=firecrawl_api_key
            )
            
            # Initialize Document Processor
            self.doc_processor = DocumentProcessor()
            
            self.mysql_vector_store = MySQLVectorStore(get_mysql_config())
            
            # st.session_state.components_initialized = True # Removed st.session_state
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            print(f"Error initializing components: {e}")  # DEBUG
            # st.session_state.components_initialized = False # Removed st.session_state
            # st.session_state.initialization_error = str(e) # Removed st.session_state
    
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
    return templates.TemplateResponse("login.html", {"request": request, "stats": stats, "active_page": None, "t": lambda key: t(key, request)})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    stats = {"total_documents": 0, "conversations": 0}
    return templates.TemplateResponse("signup.html", {"request": request, "stats": stats, "active_page": None, "t": lambda key: t(key, request)})

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    
    # Ensure user has greeting_name for personalized greeting
    if "greeting_name" not in user:
        cursor = user_store.conn.cursor(dictionary=True)
        cursor.execute("SELECT first_name, last_name FROM users WHERE id = %s", (user["id"],))
        user_details = cursor.fetchone()
        cursor.close()
        
        # Create personalized greeting
        first_name = user_details.get('first_name', '') if user_details else ''
        last_name = user_details.get('last_name', '') if user_details else ''
        
        if first_name and last_name:
            greeting_name = f"{first_name} {last_name[0].upper()}."
        elif first_name:
            greeting_name = first_name
        else:
            greeting_name = user["username"]
        
        # Update session with greeting name
        user["greeting_name"] = greeting_name
        request.session["user"] = user
    
    return user

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: dict = Depends(get_current_user)):
    # Calculate actual stats for the current user
    user_id = user["id"]
    result = safe_mysql_query(
        "SELECT COUNT(*) as total_documents FROM documents WHERE user_id = %s", 
        (user_id,), 
        fetch_one=True
    )
    total_documents = result['total_documents'] if result else 0
    
    stats = {"total_documents": total_documents, "conversations": 0}
    return templates.TemplateResponse(
        "chatgpt_dashboard.html",
        {"request": request, "user": user, "stats": stats, "active_page": "dashboard", "t": lambda key: t(key, request)}
    )

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, user: dict = Depends(get_current_user)):
    # Check if user is admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    
    # Calculate admin stats
    cursor = user_store.conn.cursor(dictionary=True)
    
    # Total users
    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()["total"]
    
    # New users this week
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
    new_users_week = cursor.fetchone()["total"]
    
    # Total documents
    cursor.execute("SELECT COUNT(*) as total FROM documents")
    total_documents = cursor.fetchone()["total"]
    
    # Recent activities (placeholder)
    recent_activities = [
        {"user_name": "John S.", "action": "Document Upload", "timestamp": "2 minutes ago"},
        {"user_name": "Sarah M.", "action": "Legal Research", "timestamp": "5 minutes ago"},
        {"user_name": "Ahmed A.", "action": "Web Research", "timestamp": "10 minutes ago"},
        {"user_name": "Lisa K.", "action": "Document Analysis", "timestamp": "15 minutes ago"},
    ]
    
    cursor.close()
    
    admin_stats = {
        "total_users": total_users,
        "new_users_week": new_users_week,
        "total_documents": total_documents,
        "system_uptime": "99.9%",
        "recent_activities": recent_activities
    }
    
    return templates.TemplateResponse(
        "chatgpt_admin_dashboard.html",
        {"request": request, "user": user, "admin_stats": admin_stats, "active_page": "admin-dashboard", "t": lambda key: t(key, request)}
    )

@app.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request, user: dict = Depends(get_current_user)):
    """Admin user management page"""
    # Check if user is admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    
    return templates.TemplateResponse(
        "chatgpt_admin_users.html",
        {"request": request, "user": user, "active_page": "admin-users", "t": lambda key: t(key, request)}
    )

@app.get("/legal-research", response_class=HTMLResponse)
def legal_research(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        "chatgpt_legal_research.html",
        {"request": request, "user": user, "active_page": "legal-research", "t": lambda key: t(key, request)}
    )

@app.get("/document-analysis", response_class=HTMLResponse)
def document_analysis(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        "chatgpt_document_analysis.html",
        {"request": request, "user": user, "active_page": "document-analysis", "t": lambda key: t(key, request)}
    )

@app.get("/knowledge-base", response_class=HTMLResponse)
def knowledge_base(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        "chatgpt_knowledge_base.html",
        {"request": request, "user": user, "active_page": "knowledge-base", "t": lambda key: t(key, request)}
    )

@app.get("/web-research", response_class=HTMLResponse)
def web_research(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(
        "chatgpt_web_research.html",
        {"request": request, "user": user, "active_page": "web-research", "t": lambda key: t(key, request)}
    )

@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request, user: dict = Depends(get_current_user)):
    # Load user settings if available
    settings_data = user.get("settings", {}) if user else {}
    current_provider = settings_data.get("llm_provider", "ollama")
    current_model = settings_data.get("llm_model", "llama3:8b")
    
    return templates.TemplateResponse(
        "chatgpt_settings.html",
        {"request": request, "user": user, "active_page": "settings", "current_provider": current_provider, "current_model": current_model, "t": lambda key: t(key, request)}
    )

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    stats = {"total_documents": 0, "conversations": 0}
    user = user_store.get_user_by_username(username)
    if not user or not pwd_context.verify(password, user['password_hash']):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "stats": stats, "active_page": None, "t": lambda key: t(key, request)})
    
    # Fetch user's first and last name for personalized greeting
    cursor = user_store.conn.cursor(dictionary=True)
    cursor.execute("SELECT first_name, last_name FROM users WHERE id = %s", (user["id"],))
    user_details = cursor.fetchone()
    cursor.close()
    
    # Create personalized greeting
    first_name = user_details.get('first_name', '') if user_details else ''
    last_name = user_details.get('last_name', '') if user_details else ''
    
    if first_name and last_name:
        greeting_name = f"{first_name} {last_name[0].upper()}."
    elif first_name:
        greeting_name = first_name
    else:
        greeting_name = user["username"]
    
    request.session["user"] = {
        "id": user["id"], 
        "username": user["username"], 
        "role": user["role"],
        "greeting_name": greeting_name
    }
    log_activity(user["id"], "login", {"username": user["username"]})
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/signup", response_class=HTMLResponse)
def signup_post(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    company_name: str = Form(...),
    job_title: str = Form(...),
    employee_id: str = Form(None),
    phone: str = Form(None),
    department: str = Form(None),
    role: str = Form("user")
):
    stats = {"total_documents": 0, "conversations": 0}
    
    # Check if username already exists
    if user_store.get_user_by_username(username):
        return templates.TemplateResponse("signup.html", {
            "request": request, 
            "error": "Username already exists.", 
            "stats": stats, 
            "active_page": None,
            "t": lambda key: t(key, request)
        })
    
    # Hash password and add user with all fields
    password_hash = pwd_context.hash(password)
    
    # Use raw SQL to insert with all fields
    cursor = user_store.conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, 
                         company_name, job_title, employee_id, phone, department, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (username, email, password_hash, first_name, last_name, 
          company_name, job_title, employee_id, phone, department, role))
    user_store.conn.commit()
    cursor.close()
    
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
def logout(request: Request):
    user = request.session.get("user")
    if user:
        log_activity(user["id"], "logout", {"username": user["username"]})
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/legal-research", response_class=HTMLResponse)
def legal_research_post(request: Request, user: dict = Depends(get_current_user), query: str = Form(...), jurisdiction: str = Form(...), include_web_search: str = Form(None), conversation_id: int = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    error = None
    research_result = None
    kb_results = []
    web_results = []
    current_conversation_id = conversation_id
    
    try:
        # Create new conversation if none provided
        if not current_conversation_id:
            # Generate a title from the query
            title = query[:50] + "..." if len(query) > 50 else query
            current_conversation_id = user_store.create_conversation(user["id"], title, "legal_research")
        
        # Add user message to conversation
        user_store.add_message_to_conversation(current_conversation_id, "user", query)
        
        llm_engine = LLMEngine.from_user_settings(user.get('settings'))
        
        # Get conversation history for context
        conversation_messages = user_store.get_conversation_messages(current_conversation_id)
        conversation_history = []
        for msg in conversation_messages[:-1]:  # Exclude the current user message
            conversation_history.append({
                "role": msg["sender_type"],
                "content": msg["message"]
            })
        
        # Try to find relevant documents in the user's knowledge base using vector search
        doc_context = None
        kb_results = []
        if query and MYSQL_AVAILABLE and user_store:
            try:
                # Use vector search to find relevant documents from user's knowledge base
                query_embedding = vector_store._generate_embedding(query)
                kb_results = user_store.search_documents(user["id"], query_embedding, top_k=5)
                
                print(f"DEBUG: Found {len(kb_results)} documents in knowledge base")
                for i, result in enumerate(kb_results):
                    print(f"DEBUG: Result {i+1}: {result.get('title', 'Untitled')} - Score: {result.get('score', 0):.3f}")
                
                if kb_results:
                    # Filter results by relevance score (threshold of 0.3)
                    relevant_results = [r for r in kb_results if r.get('score', 0) >= 0.3]
                    print(f"DEBUG: {len(relevant_results)} results above threshold 0.3")
                    if relevant_results:
                        doc_context = "=== KNOWLEDGE BASE DOCUMENTS ===\n\n"
                        doc_context += "\n\n".join([
                            f"Document: {r.get('title', 'Untitled')}\nRelevance Score: {r.get('score', 0):.3f}\nContent: {r.get('content', '')[:1500]}..."
                            for r in relevant_results[:3]  # Limit to top 3 most relevant
                        ])
                        doc_context += "\n\n=== END KNOWLEDGE BASE ===\n\n"
            except Exception as kb_error:
                print(f"Knowledge base search failed: {kb_error}")
                # Fallback to simple title matching
                try:
                    cursor = user_store._get_connection().cursor(dictionary=True)
                    cursor.execute("SELECT title, content FROM documents WHERE user_id = %s", (user["id"],))
                    docs = cursor.fetchall()
                    cursor.close()
                    for doc in docs:
                        if any(keyword.lower() in doc["title"].lower() or keyword.lower() in doc["content"].lower() 
                               for keyword in query.lower().split()):
                            doc_context = f"=== KNOWLEDGE BASE DOCUMENTS ===\n\nDocument: {doc['title']}\nContent: {doc['content'][:2000]}...\n\n=== END KNOWLEDGE BASE ===\n\n"
                            break
                except Exception as fallback_error:
                    print(f"Fallback search also failed: {fallback_error}")
        
        # If still no context found, try global vector search as last resort
        if not doc_context:
            try:
                kb_results = vector_store.search(query, n_results=3)
                if kb_results:
                    doc_context = "\n\n".join([f"Document: {r['metadata']['title']}\n{r['content'][:1000]}..." for r in kb_results])
            except Exception as global_error:
                print(f"Global vector search failed: {global_error}")
        
        # Generate response with conversation context
        print(f"DEBUG: Document context found: {bool(doc_context)}")
        if doc_context:
            print(f"DEBUG: Context preview: {doc_context[:200]}...")
        research_result = llm_engine.generate_response(query, context=doc_context, conversation_history=conversation_history)
        
        # Add AI response to conversation
        user_store.add_message_to_conversation(current_conversation_id, "assistant", research_result)
        
        # Web research (placeholder)
        if include_web_search:
            web_results = []  # Implement web scraping if needed
            
    except Exception as e:
        error = str(e)
        if current_conversation_id:
            user_store.add_message_to_conversation(current_conversation_id, "assistant", f"Error: {error}")
    
    return templates.TemplateResponse(
        "chatgpt_legal_research.html",
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
            "error": error,
            "conversation_id": current_conversation_id,
            "t": lambda key: t(key, request)
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
        "chatgpt_document_analysis.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "document-analysis",
            "analysis_result": analysis_result,
            "kb_success": kb_success,
            "error": error,
            "t": lambda key: t(key, request)
        }
    )

@app.post("/knowledge-base", response_class=HTMLResponse)
def knowledge_base_post(request: Request, user: dict = Depends(get_current_user), search_query: str = Form(...), num_results: int = Form(...), min_score: float = Form(...)):
    # Calculate actual stats for the current user
    user_id = user["id"]
    
    # Get document count
    result = safe_mysql_query(
        "SELECT COUNT(*) as total FROM documents WHERE user_id = %s", 
        (user_id,), 
        fetch_one=True
    )
    total_documents = result['total'] if result else 0
    
    # Get document types
    document_types_result = safe_mysql_query(
        "SELECT DISTINCT document_type FROM documents WHERE user_id = %s", 
        (user_id,), 
        fetch_all=True
    )
    document_types = [row["document_type"] for row in document_types_result] if document_types_result else []
    
    # Get sources
    sources_result = safe_mysql_query(
        "SELECT DISTINCT source FROM documents WHERE user_id = %s", 
        (user_id,), 
        fetch_all=True
    )
    sources = [row["source"] for row in sources_result] if sources_result else []
    
    stats = {"total_documents": total_documents, "conversations": 0, "document_types": document_types, "sources": sources}
    error = None
    results = []
    ai_analysis = None
    
    try:
        # Try MySQL vector store for user-specific search first
        if MYSQL_AVAILABLE and user_store:
            try:
                query_embedding = vector_store._generate_embedding(search_query)
                results = user_store.search_documents(user_id, query_embedding, top_k=num_results)
                # Filter by score threshold
                results = [r for r in results if r.get('score', 0) >= min_score]
            except Exception as mysql_error:
                print(f"MySQL search failed, falling back to ChromaDB: {mysql_error}")
                # Fallback to ChromaDB global search
                results = vector_store.search(search_query, n_results=num_results)
                # Filter by score threshold
                results = [r for r in results if r.get('score', 0) >= min_score]
        else:
            print("MySQL not available, using ChromaDB global search")
            # Use ChromaDB global search
            results = vector_store.search(search_query, n_results=num_results)
            # Filter by score threshold
            results = [r for r in results if r.get('score', 0) >= min_score]
        
        # Generate AI analysis if we have results
        if results and len(results) > 0:
            try:
                # Combine top results for analysis
                combined_content = "\n\n".join([f"Document: {r.get('title', 'Untitled')}\nContent: {r.get('content', '')[:1000]}" for r in results[:3]])
                ai_analysis = LLMEngine.from_user_settings(user.get('settings', {})).analyze_document(combined_content, "knowledge_base_search")
            except Exception as analysis_error:
                print(f"Error generating AI analysis: {analysis_error}")
                ai_analysis = f"Analysis temporarily unavailable: {str(analysis_error)}"
                
    except Exception as e:
        error = str(e)
        results = []
    return templates.TemplateResponse(
        "chatgpt_knowledge_base.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "knowledge-base",
            "search_query": search_query,
            "num_results": num_results,
            "min_score": min_score,
            "results": results,
            "ai_analysis": ai_analysis,
            "error": error,
            "t": lambda key: t(key, request)
        }
    )

# Find the DALIApp instance or create one if not present
if not hasattr(app, 'dali_app'):
    from src.web.app import DALIApp
    app.dali_app = DALIApp()

@app.post("/web-research", response_class=HTMLResponse)
def web_research_post(request: Request, user: dict = Depends(get_current_user), research_urls: str = Form(...), max_pages: int = Form(...), add_to_kb: str = Form(None)):
    stats = {"total_documents": 0, "conversations": 0}
    error = None
    all_results = []
    debug_results = []
    try:
        urls = [url.strip() for url in research_urls.split('\n') if url.strip()]
        for url in urls:
            # Use the DALIApp's FirecrawlScraper instance
            result = app.dali_app.scraper.scrape_url(url)
            # Clean content for plain text (remove markdown/images/links)
            content_plain = re.sub(r'!\[.*?\]\(.*?\)', '', result.content)  # Remove images
            content_plain = re.sub(r'\[.*?\]\(.*?\)', '', content_plain)    # Remove links
            content_plain = re.sub(r'<[^>]+>', '', content_plain)              # Remove HTML tags
            content_plain = re.sub(r'[#*_>`\-]', '', content_plain)           # Remove markdown symbols
            content_plain = re.sub(r'\s+', ' ', content_plain).strip()        # Collapse whitespace
            # For debugging: show the raw content and metadata (no longer sent to template)
            if result.success:
                all_results.append({
                    "title": result.title or f"Results from {url}",
                    "url": url,
                    "content": result.content or "No content extracted.",
                    "content_plain": content_plain or "No plain text extracted."
                })
                if add_to_kb:
                    # Split content into chunks for better processing
                    chunks = vector_store.text_splitter.split_text(result.content)
                    success_count = 0
                    
                    for i, chunk in enumerate(chunks):
                        metadata = create_legal_document_metadata(
                            title=f"{result.title or url} - Part {i+1}",
                            document_type="web_research",
                            source=url,
                            date_created=datetime.now().isoformat()
                        )
                        
                        embedding = vector_store._generate_embedding(chunk)
                        user_store.add_document(
                            user_id=user["id"],
                            title=f"{result.title or url} - Part {i+1}",
                            document_type="web_research",
                            source=url,
                            content=chunk,
                            embedding=np.array(embedding, dtype=np.float32),
                            metadata=metadata
                        )
                        success_count += 1
                    
                    if success_count > 0:
                        log_activity(user["id"], "web_research_added", {"url": url, "chunks": success_count})
            else:
                all_results.append({
                    "title": f"Failed to scrape {url}",
                    "url": url,
                    "content": result.error or "Unknown error.",
                    "content_plain": result.error or "Unknown error."
                })
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        "chatgpt_web_research.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "web-research",
            "research_urls": research_urls,
            "max_pages": max_pages,
            "add_to_kb": add_to_kb,
            "all_results": all_results,
            "error": error,
            "t": lambda key: t(key, request)
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
        "chatgpt_settings.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_page": "settings",
            "current_provider": settings.get("llm_provider", "ollama"),
            "current_model": settings.get("llm_model", "llama3:8b"),
            "t": lambda key: t(key, request)
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

@app.get("/api/users/all")
def api_users_all(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    try:
        users_result = safe_mysql_query(
            "SELECT id, username, last_active FROM users WHERE id != %s", 
            (user["id"],), 
            fetch_all=True
        )
        
        if not users_result:
            return {"users": []}
            
        users = users_result
        now = datetime.utcnow()
        online_cutoff = now - timedelta(minutes=5)
        for u in users:
            # If last_active is None, treat as offline
            if u.get("last_active"):
                try:
                    last_active_dt = u["last_active"]
                    if isinstance(last_active_dt, str):
                        last_active_dt = datetime.fromisoformat(last_active_dt)
                    u["online"] = last_active_dt > online_cutoff
                except Exception:
                    u["online"] = False
            else:
                u["online"] = False
        return {"users": users}
    except Exception as e:
        # Return empty users list if MySQL is not available
        print(f"MySQL connection error in api_users_all: {e}")
        return {"users": []}

@app.post("/api/language/toggle")
def api_language_toggle(request: Request):
    """Toggle language between English and Arabic"""
    current_lang = request.session.get("language", "en")
    new_lang = "ar" if current_lang == "en" else "en"
    request.session["language"] = new_lang
    return {"success": True, "language": new_lang}

# Knowledge Base API Endpoints
@app.get("/api/knowledge-base/my-documents")
def api_get_my_documents(request: Request):
    """Get all documents for the current user"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        documents = safe_mysql_query(
            "SELECT id, title, document_type, source, content, created_at FROM documents WHERE user_id = %s ORDER BY created_at DESC",
            (user["id"],),
            fetch_all=True
        )
        
        if documents is None:
            return {"documents": []}
        
        # Format documents for frontend
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "id": doc["id"],
                "title": doc["title"] or "Untitled Document",
                "document_type": doc["document_type"] or "Unknown",
                "source": doc["source"],
                "content": doc["content"],
                "created_at": doc["created_at"].isoformat() if doc["created_at"] else None
            })
        
        return {"documents": formatted_docs}
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return {"documents": []}

@app.get("/api/knowledge-base/document/{document_id}")
def api_get_document(request: Request, document_id: int):
    """Get a specific document by ID"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        document = safe_mysql_query(
            "SELECT id, title, document_type, source, content, created_at FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user["id"]),
            fetch_one=True
        )
        
        if not document:
            return {"error": "Document not found"}
        
        return {
            "id": document["id"],
            "title": document["title"],
            "document_type": document["document_type"],
            "source": document["source"],
            "content": document["content"],
            "created_at": document["created_at"].isoformat() if document["created_at"] else None
        }
    except Exception as e:
        print(f"Error fetching document: {e}")
        return {"error": "Failed to fetch document"}

@app.get("/api/knowledge-base/document/{document_id}/pdf")
def api_download_document_pdf(request: Request, document_id: int):
    """Download document as PDF"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        document = safe_mysql_query(
            "SELECT title, content FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user["id"]),
            fetch_one=True
        )
        
        if not document:
            return {"error": "Document not found"}
        
        # Generate PDF content (simplified - you might want to use a proper PDF library)
        pdf_content = f"""
Document: {document['title'] or 'Untitled'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Content:
{document['content']}
        """
        
        from fastapi.responses import Response
        return Response(
            content=pdf_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=document_{document_id}.txt"}
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return {"error": "Failed to generate PDF"}

@app.get("/document/{document_id}", response_class=HTMLResponse)
def view_document(request: Request, document_id: int):
    """View document in a formatted page"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        document = safe_mysql_query(
            "SELECT id, title, document_type, source, content, created_at FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user["id"]),
            fetch_one=True
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return templates.TemplateResponse(
            "document_view.html",
            {
                "request": request,
                "user": user,
                "document": document,
                "t": lambda key: t(key, request)
            }
        )
    except Exception as e:
        print(f"Error viewing document: {e}")
        raise HTTPException(status_code=500, detail="Error viewing document")

@app.delete("/api/knowledge-base/document/{document_id}")
def api_delete_document(request: Request, document_id: int):
    """Delete a document"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        result = safe_mysql_query(
            "DELETE FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user["id"])
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "Document not found"}
    except Exception as e:
        print(f"Error deleting document: {e}")
        return {"error": "Failed to delete document"}

@app.post("/api/knowledge-base/share")
def api_share_document(request: Request):
    """Share a document with another user"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        document_id = data.get("document_id")
        recipient_username = data.get("recipient_username")
        
        if not document_id or not recipient_username:
            return {"error": "Missing required fields"}
        
        # Get recipient user
        recipient = safe_mysql_query(
            "SELECT id FROM users WHERE username = %s",
            (recipient_username,),
            fetch_one=True
        )
        
        if not recipient:
            return {"error": "Recipient user not found"}
        
        # Check if document belongs to current user
        document = safe_mysql_query(
            "SELECT id FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user["id"]),
            fetch_one=True
        )
        
        if not document:
            return {"error": "Document not found"}
        
        # Share the document
        safe_mysql_query(
            "INSERT INTO shared_documents (document_id, shared_with_user_id, shared_by_user_id) VALUES (%s, %s, %s)",
            (document_id, recipient["id"], user["id"])
        )
        
        return {"success": True}
    except Exception as e:
        print(f"Error sharing document: {e}")
        return {"error": "Failed to share document"}

@app.get("/api/knowledge-base/export")
def api_export_knowledge_base(request: Request):
    """Export knowledge base as JSON"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        documents = safe_mysql_query(
            "SELECT id, title, document_type, source, content, created_at FROM documents WHERE user_id = %s ORDER BY created_at DESC",
            (user["id"],),
            fetch_all=True
        )
        
        if documents is None:
            documents = []
        
        export_data = {
            "user_id": user["id"],
            "username": user["username"],
            "export_date": datetime.now().isoformat(),
            "documents": documents
        }
        
        from fastapi.responses import Response
        import json
        
        return Response(
            content=json.dumps(export_data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=knowledge-base-export.json"}
        )
    except Exception as e:
        print(f"Error exporting knowledge base: {e}")
        return {"error": "Failed to export knowledge base"}

# Admin API Endpoints
@app.get("/api/admin/users")
def api_admin_get_users(request: Request):
    """Get all users for admin management"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        users = safe_mysql_query(
            "SELECT id, username, email, role, is_active, last_active, created_at FROM users ORDER BY created_at DESC",
            fetch_all=True
        )
        
        if users is None:
            return {"users": []}
        
        # Format users for frontend
        formatted_users = []
        for u in users:
            formatted_users.append({
                "id": u["id"],
                "username": u["username"],
                "email": u["email"],
                "role": u["role"],
                "is_active": bool(u["is_active"]),
                "last_active": u["last_active"].isoformat() if u["last_active"] else None,
                "created_at": u["created_at"].isoformat() if u["created_at"] else None
            })
        
        return {"users": formatted_users}
    except Exception as e:
        print(f"Error fetching users: {e}")
        return {"users": []}

@app.get("/api/admin/users/{user_id}")
def api_admin_get_user(request: Request, user_id: int):
    """Get a specific user by ID for admin"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        user_data = safe_mysql_query(
            "SELECT id, username, email, role, is_active, last_active, created_at, first_name, last_name, company_name, job_title, employee_id, phone, department FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        if not user_data:
            return {"error": "User not found"}
        
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"],
            "is_active": bool(user_data["is_active"]),
            "last_active": user_data["last_active"].isoformat() if user_data["last_active"] else None,
            "created_at": user_data["created_at"].isoformat() if user_data["created_at"] else None,
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "company_name": user_data["company_name"],
            "job_title": user_data["job_title"],
            "employee_id": user_data["employee_id"],
            "phone": user_data["phone"],
            "department": user_data["department"]
        }
    except Exception as e:
        print(f"Error fetching user: {e}")
        return {"error": "Failed to fetch user"}

@app.post("/api/admin/users/{user_id}/toggle-status")
def api_admin_toggle_user_status(request: Request, user_id: int):
    """Toggle user active status"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        data = request.json()
        action = data.get("action")
        
        if action not in ["ban", "activate"]:
            return {"error": "Invalid action"}
        
        new_status = action == "activate"
        
        result = safe_mysql_query(
            "UPDATE users SET is_active = %s WHERE id = %s",
            (new_status, user_id)
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "User not found"}
    except Exception as e:
        print(f"Error toggling user status: {e}")
        return {"error": "Failed to update user status"}

@app.delete("/api/admin/users/{user_id}")
def api_admin_delete_user(request: Request, user_id: int):
    """Delete a user"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        # Don't allow admin to delete themselves
        if user["id"] == user_id:
            return {"error": "Cannot delete your own account"}
        
        result = safe_mysql_query(
            "DELETE FROM users WHERE id = %s",
            (user_id,)
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "User not found"}
    except Exception as e:
        print(f"Error deleting user: {e}")
        return {"error": "Failed to delete user"}

@app.post("/api/admin/users/bulk-activate")
def api_admin_bulk_activate_users(request: Request):
    """Bulk activate users"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        data = request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {"error": "No users selected"}
        
        placeholders = ",".join(["%s"] * len(user_ids))
        result = safe_mysql_query(
            f"UPDATE users SET is_active = 1 WHERE id IN ({placeholders})",
            user_ids
        )
        
        return {"success": True, "updated": result}
    except Exception as e:
        print(f"Error bulk activating users: {e}")
        return {"error": "Failed to activate users"}

@app.post("/api/admin/users/bulk-deactivate")
def api_admin_bulk_deactivate_users(request: Request):
    """Bulk deactivate users"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        data = request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {"error": "No users selected"}
        
        placeholders = ",".join(["%s"] * len(user_ids))
        result = safe_mysql_query(
            f"UPDATE users SET is_active = 0 WHERE id IN ({placeholders})",
            user_ids
        )
        
        return {"success": True, "updated": result}
    except Exception as e:
        print(f"Error bulk deactivating users: {e}")
        return {"error": "Failed to deactivate users"}

@app.post("/api/admin/users/bulk-delete")
def api_admin_bulk_delete_users(request: Request):
    """Bulk delete users"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        data = request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {"error": "No users selected"}
        
        # Don't allow admin to delete themselves
        if user["id"] in user_ids:
            return {"error": "Cannot delete your own account"}
        
        placeholders = ",".join(["%s"] * len(user_ids))
        result = safe_mysql_query(
            f"DELETE FROM users WHERE id IN ({placeholders})",
            user_ids
        )
        
        return {"success": True, "deleted": result}
    except Exception as e:
        print(f"Error bulk deleting users: {e}")
        return {"error": "Failed to delete users"}

@app.post("/api/admin/users/bulk-change-role")
def api_admin_bulk_change_role(request: Request):
    """Bulk change user roles"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        data = request.json()
        user_ids = data.get("user_ids", [])
        new_role = data.get("new_role")
        
        if not user_ids or not new_role:
            return {"error": "Missing required fields"}
        
        if new_role not in ["user", "admin"]:
            return {"error": "Invalid role"}
        
        placeholders = ",".join(["%s"] * len(user_ids))
        result = safe_mysql_query(
            f"UPDATE users SET role = %s WHERE id IN ({placeholders})",
            [new_role] + user_ids
        )
        
        return {"success": True, "updated": result}
    except Exception as e:
        print(f"Error bulk changing roles: {e}")
        return {"error": "Failed to change user roles"}

@app.get("/api/admin/users/export")
def api_admin_export_users(request: Request):
    """Export all users as JSON"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return {"error": "Access denied. Admin role required."}
    
    try:
        users = safe_mysql_query(
            "SELECT id, username, email, role, is_active, last_active, created_at, first_name, last_name, company_name, job_title, employee_id, phone, department FROM users ORDER BY created_at DESC",
            fetch_all=True
        )
        
        if users is None:
            users = []
        
        export_data = {
            "exported_by": user["username"],
            "export_date": datetime.now().isoformat(),
            "total_users": len(users),
            "users": users
        }
        
        from fastapi.responses import Response
        import json
        
        return Response(
            content=json.dumps(export_data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=users-export.json"}
        )
    except Exception as e:
        print(f"Error exporting users: {e}")
        return {"error": "Failed to export users"}

# User Profile API Endpoints
@app.post("/api/user/profile/update")
def api_update_user_profile(request: Request):
    """Update user profile information"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        
        # Validate required fields
        if not data.get("first_name") or not data.get("last_name"):
            return {"error": "First name and last name are required"}
        
        # Update user profile
        result = safe_mysql_query(
            """UPDATE users SET 
                first_name = %s, 
                last_name = %s, 
                company_name = %s, 
                job_title = %s, 
                employee_id = %s, 
                phone = %s, 
                department = %s 
            WHERE id = %s""",
            (
                data.get("first_name"),
                data.get("last_name"),
                data.get("company_name"),
                data.get("job_title"),
                data.get("employee_id"),
                data.get("phone"),
                data.get("department"),
                user["id"]
            )
        )
        
        if result > 0:
            # Update session with new greeting name
            greeting_name = f"{data.get('first_name')} {data.get('last_name', '')[:1]}."
            request.session["greeting_name"] = greeting_name
            
            return {"success": True, "greeting_name": greeting_name}
        else:
            return {"error": "Failed to update profile"}
    except Exception as e:
        print(f"Error updating profile: {e}")
        return {"error": "Failed to update profile"}

@app.post("/api/user/greeting/update")
def api_update_greeting_name(request: Request):
    """Update greeting name in session"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if first_name and last_name:
            greeting_name = f"{first_name} {last_name[:1]}."
        elif first_name:
            greeting_name = first_name
        else:
            greeting_name = user["username"]
        
        request.session["greeting_name"] = greeting_name
        
        return {"success": True, "greeting_name": greeting_name}
    except Exception as e:
        print(f"Error updating greeting name: {e}")
        return {"error": "Failed to update greeting name"}

@app.post("/api/user/password/change")
def api_change_password(request: Request):
    """Change user password"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        if not current_password or not new_password:
            return {"error": "Current password and new password are required"}
        
        if len(new_password) < 6:
            return {"error": "New password must be at least 6 characters long"}
        
        # Verify current password
        import bcrypt
        user_data = safe_mysql_query(
            "SELECT password_hash FROM users WHERE id = %s",
            (user["id"],),
            fetch_one=True
        )
        
        if not user_data:
            return {"error": "User not found"}
        
        # Check current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user_data["password_hash"].encode('utf-8')):
            return {"error": "Current password is incorrect"}
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        result = safe_mysql_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user["id"])
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "Failed to update password"}
    except Exception as e:
        print(f"Error changing password: {e}")
        return {"error": "Failed to change password"}

# Document Analysis API Endpoints
@app.post("/api/document-analysis/share")
def api_share_document_analysis(request: Request):
    """Share document analysis with another user"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        recipient_username = data.get("recipient_username")
        analysis_text = data.get("analysis_text")
        document_title = data.get("document_title")
        
        if not recipient_username or not analysis_text:
            return {"error": "Missing required fields"}
        
        # Get recipient user
        recipient = safe_mysql_query(
            "SELECT id FROM users WHERE username = %s",
            (recipient_username,),
            fetch_one=True
        )
        
        if not recipient:
            return {"error": "Recipient user not found"}
        
        # Add analysis to recipient's knowledge base
        result = safe_mysql_query(
            """INSERT INTO documents (user_id, title, document_type, source, content, metadata) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                recipient["id"],
                f"Shared Analysis: {document_title}",
                "analysis",
                "shared_analysis",
                analysis_text,
                f'{{"shared_by": "{user["username"]}", "original_title": "{document_title}"}}'
            )
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "Failed to share analysis"}
    except Exception as e:
        print(f"Error sharing analysis: {e}")
        return {"error": "Failed to share analysis"}

@app.post("/api/knowledge-base/add-analysis")
def api_add_analysis_to_kb(request: Request):
    """Add analysis to user's knowledge base"""
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    try:
        data = request.json()
        title = data.get("title")
        content = data.get("content")
        document_type = data.get("document_type", "analysis")
        source = data.get("source", "document_analysis")
        
        if not title or not content:
            return {"error": "Title and content are required"}
        
        # Add to knowledge base
        result = safe_mysql_query(
            """INSERT INTO documents (user_id, title, document_type, source, content, metadata) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                user["id"],
                title,
                document_type,
                source,
                content,
                '{"added_from": "document_analysis"}'
            )
        )
        
        if result > 0:
            return {"success": True}
        else:
            return {"error": "Failed to add to knowledge base"}
    except Exception as e:
        print(f"Error adding to knowledge base: {e}")
        return {"error": "Failed to add to knowledge base"}

@app.post("/api/user/update_activity")
def api_update_activity(request: Request):
    """Update user's last activity timestamp"""
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    try:
        result = safe_mysql_query(
            "UPDATE users SET last_active = NOW() WHERE id = %s", 
            (user["id"],)
        )
        return {"success": True}
    except Exception as e:
        # Return success even if MySQL is not available
        print(f"MySQL connection error in api_update_activity: {e}")
        return {"success": True}

@app.get("/api/conversations")
def api_get_conversations(request: Request, user: dict = Depends(get_current_user)):
    """Get all conversations for the current user"""
    try:
        conversations = user_store.get_user_conversations(user["id"])
        return {"conversations": conversations}
    except Exception as e:
        print(f"MySQL connection error in api_get_conversations: {e}")
        return {"conversations": []}

@app.post("/api/conversations")
def api_create_conversation(request: Request, user: dict = Depends(get_current_user), title: str = Form(...), conversation_type: str = Form("legal_research")):
    """Create a new conversation"""
    conversation_id = user_store.create_conversation(user["id"], title, conversation_type)
    return {"conversation_id": conversation_id, "success": True}

@app.get("/api/conversations/{conversation_id}/messages")
def api_get_conversation_messages(conversation_id: int, request: Request, user: dict = Depends(get_current_user)):
    """Get all messages for a specific conversation"""
    messages = user_store.get_conversation_messages(conversation_id)
    return {"messages": messages}

@app.post("/api/conversations/{conversation_id}/messages")
def api_add_message_to_conversation(conversation_id: int, request: Request, user: dict = Depends(get_current_user), sender_type: str = Form(...), message: str = Form(...)):
    """Add a message to a conversation"""
    user_store.add_message_to_conversation(conversation_id, sender_type, message)
    return {"success": True}

@app.put("/api/conversations/{conversation_id}/title")
def api_update_conversation_title(conversation_id: int, request: Request, user: dict = Depends(get_current_user), new_title: str = Form(...)):
    """Update conversation title"""
    user_store.update_conversation_title(conversation_id, new_title)
    return {"success": True}

@app.delete("/api/conversations/{conversation_id}")
def api_delete_conversation(conversation_id: int, request: Request, user: dict = Depends(get_current_user)):
    """Delete a conversation"""
    user_store.delete_conversation(conversation_id)
    return {"success": True}

if __name__ == "__main__":
    # Initialize and run the application
    app = DALIApp()
    app.run()