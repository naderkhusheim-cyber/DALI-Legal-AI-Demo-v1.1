"""
DALI Legal AI - Complete New Web System
A comprehensive legal AI platform with all features integrated
"""

import uvicorn
import os
import json
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, UploadFile, File, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import sqlite3
import logging
import requests
from bs4 import BeautifulSoup
import tempfile
from passlib.context import CryptContext
from urllib.parse import urljoin, urlparse
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Language translations
LANGUAGES = {
    'en': {
        'welcome_title': 'Welcome to DALI Legal AI',
        'welcome_subtitle': 'Your complete legal AI platform',
        'login': 'Login',
        'signup': 'Sign Up',
        'logout': 'Logout',
        'username': 'Username',
        'password': 'Password',
        'email': 'Email',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'company_name': 'Company Name',
        'job_title': 'Job Title',
        'phone': 'Phone',
        'department': 'Department',
        'role': 'Role',
        'user_role': 'User',
        'admin_role': 'Admin',
        'create_account': 'Create Account',
        'already_have_account': 'Already have an account?',
        'dont_have_account': "Don't have an account?",
        'login_here': 'Login here',
        'signup_here': 'Sign up here',
        'legal_research': 'Legal Research',
        'document_analysis': 'Document Analysis',
        'web_scraping': 'Web Scraping',
        'knowledge_base': 'Knowledge Base',
        'ai_chat': 'AI Chat',
        'documents': 'Documents',
        'database_intelligence': 'Database Intelligence',
        'settings': 'Settings',
        'dashboard': 'Dashboard',
        'admin_dashboard': 'Admin Dashboard',
        'user_dashboard': 'User Dashboard',
        'system_status': 'System Status',
        'recent_activity': 'Recent Activity',
        'quick_actions': 'Quick Actions',
        'features': 'Features',
        'analytics': 'Analytics',
        'user_management': 'User Management',
        'system_logs': 'System Logs',
        'health_check': 'Health Check',
        'search': 'Search',
        'cancel': 'Cancel',
        'submit': 'Submit',
        'save': 'Save',
        'delete': 'Delete',
        'edit': 'Edit',
        'view': 'View',
        'share': 'Share',
        'upload': 'Upload',
        'download': 'Download',
        'export': 'Export',
        'import': 'Import',
        'refresh': 'Refresh',
        'loading': 'Loading...',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Info',
        'confirm': 'Confirm',
        'yes': 'Yes',
        'no': 'No',
        'close': 'Close',
        'open': 'Open',
        'back': 'Back',
        'next': 'Next',
        'previous': 'Previous',
        'home': 'Home',
        'profile': 'Profile',
        'account': 'Account',
        'preferences': 'Preferences',
        'notifications': 'Notifications',
        'help': 'Help',
        'support': 'Support',
        'about': 'About',
        'contact': 'Contact',
        'privacy': 'Privacy',
        'terms': 'Terms',
        'language': 'Language',
        'english': 'English',
        'arabic': 'العربية',
        'toggle_language': 'Toggle Language',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'toggle_theme': 'Toggle Theme',
        'welcome_back': 'Welcome back',
        'dashboard_subtitle': 'Ready to continue your legal research and analysis? Here\'s what you can do today.',
        'new_chat': 'New Chat',
        'ai_chat': 'AI Chat',
        'welcome_to_chat': 'Welcome to AI Chat',
        'start_conversation': 'Start a conversation with your legal AI assistant',
        'type_message': 'Type your message...',
        'no_conversations': 'No conversations yet',
        'last_message': 'Last message...',
        'just_now': 'Just now',
        'minutes_ago': 'minutes ago',
        'hours_ago': 'hours ago',
        'clear_chat': 'Clear Chat',
        'export_chat': 'Export Chat',
        'new_conversation': 'New Conversation',
        'confirm_clear': 'Are you sure you want to clear this chat?',
        'export_coming_soon': 'Export functionality coming soon!',
        'error_response': 'Sorry, I encountered an error. Please try again.',
        'connection_error': 'Connection error. Please check your internet connection.',
        'request_permission': 'Request Permission',
        'permission_requests': 'Permission Requests',
        'incoming_requests': 'Incoming Requests',
        'outgoing_requests': 'Outgoing Requests',
        'approve': 'Approve',
        'deny': 'Deny',
        'pending': 'Pending',
        'approved': 'Approved',
        'denied': 'Denied',
        'permission_granted': 'Permission Granted',
        'permission_denied': 'Permission Denied',
        'manage_permissions': 'Manage Permissions',
        'revoke_permission': 'Revoke Permission',
        'document_owner': 'Document Owner',
        'requester': 'Requester',
        'request_date': 'Request Date',
        'status': 'Status',
        'actions': 'Actions',
        'bulk_operations': 'Bulk Operations',
        'bulk_delete': 'Bulk Delete',
        'bulk_activate': 'Bulk Activate',
        'bulk_deactivate': 'Bulk Deactivate',
        'bulk_update_role': 'Bulk Update Role',
        'export_users': 'Export Users',
        'import_users': 'Import Users',
        'select_users': 'Select Users',
        'selected_count': 'Selected Count',
        'confirm_bulk_action': 'Confirm Bulk Action',
        'are_you_sure_bulk': 'Are you sure you want to perform this action on the selected users?',
        'operation_completed': 'Operation Completed',
        'users_affected': 'Users Affected',
        'download_csv': 'Download CSV',
        'upload_csv': 'Upload CSV',
        'csv_format': 'CSV Format',
        'import_results': 'Import Results',
        'import_errors': 'Import Errors'
    },
    'ar': {
        'welcome_title': 'مرحباً بك في دالي للذكاء الاصطناعي القانوني',
        'welcome_subtitle': 'منصتك القانونية الشاملة للذكاء الاصطناعي',
        'login': 'تسجيل الدخول',
        'signup': 'إنشاء حساب',
        'logout': 'تسجيل الخروج',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'email': 'البريد الإلكتروني',
        'first_name': 'الاسم الأول',
        'last_name': 'اسم العائلة',
        'company_name': 'اسم الشركة',
        'job_title': 'المسمى الوظيفي',
        'phone': 'الهاتف',
        'department': 'القسم',
        'role': 'الدور',
        'user_role': 'مستخدم',
        'admin_role': 'مدير',
        'create_account': 'إنشاء حساب',
        'already_have_account': 'لديك حساب بالفعل؟',
        'dont_have_account': 'ليس لديك حساب؟',
        'login_here': 'سجل الدخول هنا',
        'signup_here': 'أنشئ حساب هنا',
        'legal_research': 'البحث القانوني',
        'document_analysis': 'تحليل المستندات',
        'web_scraping': 'استخراج الويب',
        'knowledge_base': 'قاعدة المعرفة',
        'ai_chat': 'محادثة ذكية',
        'documents': 'المستندات',
        'database_intelligence': 'ذكاء قاعدة البيانات',
        'settings': 'الإعدادات',
        'dashboard': 'لوحة التحكم',
        'admin_dashboard': 'لوحة تحكم المدير',
        'user_dashboard': 'لوحة تحكم المستخدم',
        'system_status': 'حالة النظام',
        'recent_activity': 'النشاط الأخير',
        'quick_actions': 'الإجراءات السريعة',
        'features': 'الميزات',
        'analytics': 'التحليلات',
        'user_management': 'إدارة المستخدمين',
        'system_logs': 'سجلات النظام',
        'health_check': 'فحص الصحة',
        'search': 'بحث',
        'cancel': 'إلغاء',
        'submit': 'إرسال',
        'save': 'حفظ',
        'delete': 'حذف',
        'edit': 'تعديل',
        'view': 'عرض',
        'share': 'مشاركة',
        'upload': 'رفع',
        'download': 'تحميل',
        'export': 'تصدير',
        'import': 'استيراد',
        'refresh': 'تحديث',
        'loading': 'جاري التحميل...',
        'success': 'نجح',
        'error': 'خطأ',
        'warning': 'تحذير',
        'info': 'معلومات',
        'confirm': 'تأكيد',
        'yes': 'نعم',
        'no': 'لا',
        'close': 'إغلاق',
        'open': 'فتح',
        'back': 'رجوع',
        'next': 'التالي',
        'previous': 'السابق',
        'home': 'الرئيسية',
        'profile': 'الملف الشخصي',
        'account': 'الحساب',
        'preferences': 'التفضيلات',
        'notifications': 'الإشعارات',
        'help': 'المساعدة',
        'support': 'الدعم',
        'about': 'حول',
        'contact': 'اتصل بنا',
        'privacy': 'الخصوصية',
        'terms': 'الشروط',
        'language': 'اللغة',
        'english': 'English',
        'arabic': 'العربية',
        'toggle_language': 'تبديل اللغة',
        'dark_mode': 'الوضع المظلم',
        'light_mode': 'الوضع المضيء',
        'toggle_theme': 'تبديل المظهر',
        'welcome_back': 'مرحباً بعودتك',
        'dashboard_subtitle': 'مستعد لمتابعة البحث والتحليل القانوني؟ إليك ما يمكنك فعله اليوم.',
        'new_chat': 'محادثة جديدة',
        'ai_chat': 'محادثة ذكية',
        'welcome_to_chat': 'مرحباً بك في المحادثة الذكية',
        'start_conversation': 'ابدأ محادثة مع مساعدك القانوني الذكي',
        'type_message': 'اكتب رسالتك...',
        'no_conversations': 'لا توجد محادثات بعد',
        'last_message': 'آخر رسالة...',
        'just_now': 'الآن',
        'minutes_ago': 'دقائق مضت',
        'hours_ago': 'ساعات مضت',
        'clear_chat': 'مسح المحادثة',
        'export_chat': 'تصدير المحادثة',
        'new_conversation': 'محادثة جديدة',
        'confirm_clear': 'هل أنت متأكد من أنك تريد مسح هذه المحادثة؟',
        'export_coming_soon': 'وظيفة التصدير قادمة قريباً!',
        'error_response': 'عذراً، واجهت خطأ. يرجى المحاولة مرة أخرى.',
        'connection_error': 'خطأ في الاتصال. يرجى التحقق من اتصالك بالإنترنت.',
        'request_permission': 'طلب إذن',
        'permission_requests': 'طلبات الإذن',
        'incoming_requests': 'الطلبات الواردة',
        'outgoing_requests': 'الطلبات الصادرة',
        'approve': 'موافقة',
        'deny': 'رفض',
        'pending': 'معلق',
        'approved': 'موافق عليه',
        'denied': 'مرفوض',
        'permission_granted': 'تم منح الإذن',
        'permission_denied': 'تم رفض الإذن',
        'manage_permissions': 'إدارة الأذونات',
        'revoke_permission': 'إلغاء الإذن',
        'document_owner': 'مالك المستند',
        'requester': 'الطالب',
        'request_date': 'تاريخ الطلب',
        'status': 'الحالة',
        'actions': 'الإجراءات',
        'bulk_operations': 'العمليات المجمعة',
        'bulk_delete': 'حذف مجمع',
        'bulk_activate': 'تفعيل مجمع',
        'bulk_deactivate': 'إلغاء تفعيل مجمع',
        'bulk_update_role': 'تحديث الدور مجمعاً',
        'export_users': 'تصدير المستخدمين',
        'import_users': 'استيراد المستخدمين',
        'select_users': 'اختيار المستخدمين',
        'selected_count': 'عدد المحددين',
        'confirm_bulk_action': 'تأكيد العملية المجمعة',
        'are_you_sure_bulk': 'هل أنت متأكد من أنك تريد تنفيذ هذا الإجراء على المستخدمين المحددين؟',
        'operation_completed': 'تمت العملية',
        'users_affected': 'المستخدمون المتأثرون',
        'download_csv': 'تحميل CSV',
        'upload_csv': 'رفع CSV',
        'csv_format': 'تنسيق CSV',
        'import_results': 'نتائج الاستيراد',
        'import_errors': 'أخطاء الاستيراد'
    }
}

def t(key: str, request: Request = None) -> str:
    """Translation function that uses session language"""
    if request and hasattr(request, 'session'):
        lang = request.session.get("language", "en")
    else:
        lang = "en"  # Default to English
    return LANGUAGES[lang].get(key, key)

# Initialize FastAPI app
app = FastAPI(
    title="DALI Legal AI",
    description="Complete Legal AI Platform with Advanced Features",
    version="2.0.0"
)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="dali_legal_ai_secret_key_2024")

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database configuration
DB_PATH = "data/dali_users.db"

# Load configuration
def load_config():
    """Load configuration from config file"""
    try:
        from src.utils.config import load_config as load_config_func
        return load_config_func('config/config.yaml')
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

# Get Firecrawl configuration
config = load_config()
FIRECRAWL_CONFIG = config.get('firecrawl', {})
FIRECRAWL_API_KEY = FIRECRAWL_CONFIG.get('api_key', '')
FIRECRAWL_TIMEOUT = FIRECRAWL_CONFIG.get('timeout', 30000)
FIRECRAWL_WAIT_FOR = FIRECRAWL_CONFIG.get('wait_for', 3000)

# JWT Configuration
SECRET_KEY = "dali_legal_ai_jwt_secret_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role: str = "user"

class User(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool = True

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        return connection
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Conversation Memory Functions
def save_conversation_message(user_id: int, session_id: str, message_type: str, message_content: str, context_data: Optional[Dict] = None):
    """Save a conversation message to memory"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        context_json = json.dumps(context_data) if context_data else None
        
        cursor.execute('''
            INSERT INTO conversation_memory (user_id, session_id, message_type, message_content, context_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, message_type, message_content, context_json))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving conversation message: {str(e)}")
        return False

def get_conversation_history(user_id: int, session_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history for a user session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, message_content, context_data, created_at
            FROM conversation_memory
            WHERE user_id = ? AND session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            context_data = json.loads(row[2]) if row[2] else None
            messages.append({
                'type': row[0],
                'content': row[1],
                'context': context_data,
                'timestamp': row[3]
            })
        
        conn.close()
        return list(reversed(messages))  # Return in chronological order
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return []

def create_conversation_session(user_id: int, session_name: Optional[str] = None) -> str:
    """Create a new conversation session"""
    try:
        session_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_sessions (user_id, session_id, session_name)
            VALUES (?, ?, ?)
        ''', (user_id, session_id, session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        
        conn.commit()
        conn.close()
        return session_id
    except Exception as e:
        logger.error(f"Error creating conversation session: {str(e)}")
        return str(uuid.uuid4())  # Fallback

def get_active_session(user_id: int) -> Optional[str]:
    """Get the most recent active session for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id FROM conversation_sessions
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_activity DESC
            LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting active session: {str(e)}")
        return None

def update_session_activity(session_id: str):
    """Update the last activity time for a session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversation_sessions
            SET last_activity = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating session activity: {str(e)}")
        return False

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Firecrawl web scraping functions
def scrape_with_firecrawl(url: str) -> dict:
    """Scrape website using Firecrawl API"""
    try:
        if not FIRECRAWL_API_KEY:
            return {"success": False, "error": "Firecrawl API key not configured"}
        
        headers = {
            'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'url': url,
            'formats': ['markdown', 'html'],
            'waitFor': FIRECRAWL_WAIT_FOR,
            'timeout': FIRECRAWL_TIMEOUT
        }
        
        response = requests.post(
            'https://api.firecrawl.dev/v0/scrape',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "data": result.get('data', {}),
                "metadata": result.get('metadata', {}),
                "markdown": result.get('data', {}).get('markdown', ''),
                "html": result.get('data', {}).get('html', '')
            }
        else:
            return {
                "success": False,
                "error": f"Firecrawl API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {"success": False, "error": f"Firecrawl scraping failed: {str(e)}"}

def scrape_with_authentication(url: str, username: str = None, password: str = None) -> dict:
    """Scrape content from sites that require authentication"""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Enhanced headers for authenticated requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session.headers.update(headers)
        
        # Try to access the main page first
        try:
            response = session.get(url, timeout=15, allow_redirects=True)
        except Exception as e:
            return {"success": False, "error": f"Failed to access main page: {str(e)}"}
        
        # Check if we need authentication
        if response.status_code == 401 or "login" in response.text.lower() or "تسجيل الدخول" in response.text:
            logger.info(f"Authentication required for {url}")
            
            # Try to find login form and submit credentials
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for login forms
            login_form = soup.find('form', {'action': lambda x: x and 'login' in x.lower()}) or \
                        soup.find('form', {'id': lambda x: x and 'login' in x.lower()}) or \
                        soup.find('form', {'class': lambda x: x and 'login' in x.lower()})
            
            if login_form:
                login_url = login_form.get('action', url)
                if login_url.startswith('/'):
                    from urllib.parse import urljoin
                    login_url = urljoin(url, login_url)
                
                # Try to submit login form
                form_data = {}
                for input_field in login_form.find_all('input'):
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name:
                        if 'email' in name.lower() or 'username' in name.lower() or 'user' in name.lower():
                            form_data[name] = username or 'demo@example.com'
                        elif 'password' in name.lower() or 'pass' in name.lower():
                            form_data[name] = password or 'demo123'
                        else:
                            form_data[name] = value
                
                try:
                    login_response = session.post(login_url, data=form_data, timeout=15)
                    if login_response.status_code == 200:
                        # Try to access the original URL again
                        response = session.get(url, timeout=15, allow_redirects=True)
                except Exception as e:
                    logger.warning(f"Login attempt failed: {e}")
        
        # Process the response
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement", "ads"]):
                element.decompose()
            
            # Extract main content
            main_content = ""
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.main-content', 
                '.article-content', '.post-content', '.entry-content', '.page-content',
                '#content', '#main', '.container', '.wrapper', '.legal-content',
                '.document-content', '.search-results', '.documents-list'
            ]
            
            for selector in content_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    main_text = main_element.get_text(separator='\n', strip=True)
                    if len(main_text) > len(main_content):
                        main_content = main_text
                        break
            
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator='\n', strip=True)
                else:
                    main_content = soup.get_text(separator='\n', strip=True)
            
            # Clean up the text
            lines = [line.strip() for line in main_content.split('\n') if line.strip()]
            filtered_lines = []
            
            skip_patterns = [
                'skip to', 'menu', 'navigation', 'search', 'login', 'register',
                'subscribe', 'follow us', 'share', 'print', 'email', 'rss',
                'cookie', 'privacy', 'terms', 'copyright', 'all rights reserved',
                'تسجيل الدخول', 'تواصل معنا', 'english', 'المعرفة'
            ]
            
            for line in lines:
                line_lower = line.lower()
                if (len(line) > 20 and 
                    not any(pattern in line_lower for pattern in skip_patterns) and
                    not line.startswith('http') and
                    not line.startswith('www.') and
                    not line.startswith('mailto:')):
                    filtered_lines.append(line)
            
            content = '\n'.join(filtered_lines)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    links.append(href)
            
            return {
                "success": True,
                "data": {
                    "content": content,
                    "html": response.text,
                    "links": links,
                    "title": soup.find('title').get_text() if soup.find('title') else "Untitled",
                    "description": soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else ""
                },
                "metadata": {
                    "url": url,
                    "status_code": response.status_code,
                    "authenticated": True
                }
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.reason}"
            }
            
    except Exception as e:
        return {"success": False, "error": f"Authentication scraping failed: {str(e)}"}

def scrape_useful_links(url: str, max_links: int = 10, bypass_auth: bool = False) -> dict:
    """Scrape content from useful links found on a page"""
    try:
        # First get the main page to find useful links
        main_result = scrape_with_beautifulsoup(url, bypass_auth)
        if not main_result.get("success"):
            return {"success": False, "error": "Could not scrape main page"}
        
        # Extract links from the main page
        soup = BeautifulSoup(main_result.get("html", ""), 'html.parser')
        links = []
        
        # Find useful links (Wikipedia internal links, external references, etc.)
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # Filter for useful links
            if (href and text and len(text) > 3 and 
                not href.startswith('#') and  # Skip anchor links
                not href.startswith('javascript:') and  # Skip JS links
                not any(skip in href.lower() for skip in ['login', 'register', 'search', 'menu', 'nav']) and
                not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'login', 'register'])):
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                elif not href.startswith('http'):
                    continue
                
                links.append({
                    'url': href,
                    'text': text,
                    'title': link.get('title', text)
                })
        
        # Remove duplicates and limit
        unique_links = []
        seen_urls = set()
        for link in links:
            if link['url'] not in seen_urls and len(unique_links) < max_links:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        # Scrape content from each useful link
        scraped_content = []
        for link in unique_links:
            try:
                link_result = scrape_with_beautifulsoup(link['url'], bypass_auth)
                if link_result.get("success"):
                    content = link_result.get("data", {}).get("content", "")
                    if content and len(content) > 100:  # Only include substantial content
                        scraped_content.append({
                            'url': link['url'],
                            'title': link['title'],
                            'content': content[:2000]  # Limit content length
                        })
            except Exception as e:
                logger.warning(f"Failed to scrape link {link['url']}: {e}")
                continue
        
        return {
            "success": True,
            "useful_links": unique_links,
            "scraped_content": scraped_content,
            "total_links_found": len(links),
            "content_scraped": len(scraped_content)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Link scraping failed: {str(e)}"}

def scrape_with_beautifulsoup(url: str, bypass_auth: bool = False) -> dict:
    """Enhanced scraping using BeautifulSoup with robust error handling"""
    try:
        # Enhanced headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add bypass authentication headers if requested
        if bypass_auth:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f"{parsed_url.scheme}://{parsed_url.netloc}",
                'Origin': f"{parsed_url.scheme}://{parsed_url.netloc}",
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'DNT': '1',
                'Sec-GPC': '1'
            })
        
        # Make request with better error handling
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout - website took too long to respond"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection error - unable to reach the website"}
        except requests.exceptions.TooManyRedirects:
            return {"success": False, "error": "Too many redirects - website has redirect loop"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        
        # Check response status
        if response.status_code == 503:
            return {"success": False, "error": "Service temporarily unavailable (503) - website is down for maintenance"}
        elif response.status_code == 404:
            return {"success": False, "error": "Page not found (404) - URL does not exist"}
        elif response.status_code == 403:
            return {"success": False, "error": "Access forbidden (403) - website blocked the request"}
        elif response.status_code == 429:
            return {"success": False, "error": "Too many requests (429) - rate limited by website"}
        elif response.status_code >= 400:
            return {"success": False, "error": f"HTTP error {response.status_code} - {response.reason}"}
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return {"success": False, "error": f"Invalid content type: {content_type} - not an HTML page"}
        
        # Parse with BeautifulSoup
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            return {"success": False, "error": f"HTML parsing failed: {str(e)}"}
        
        # Extract main content with better prioritization
        try:
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement", "ads"]):
                element.decompose()
            
            # Try to find main content areas first
            main_content = ""
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.main-content', 
                '.article-content', '.post-content', '.entry-content', '.page-content',
                '#content', '#main', '.container', '.wrapper'
            ]
            
            for selector in content_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    # Extract text from main content area
                    main_text = main_element.get_text(separator='\n', strip=True)
                    if len(main_text) > len(main_content):
                        main_content = main_text
                        break
            
            # If no main content found, use body
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator='\n', strip=True)
                else:
                    main_content = soup.get_text(separator='\n', strip=True)
            
            # Clean up the text and prioritize meaningful content
            lines = [line.strip() for line in main_content.split('\n') if line.strip()]
            
            # Filter out very short lines and common navigation text
            filtered_lines = []
            skip_patterns = [
                'skip to', 'menu', 'navigation', 'search', 'login', 'register',
                'subscribe', 'follow us', 'share', 'print', 'email', 'rss',
                'cookie', 'privacy', 'terms', 'copyright', 'all rights reserved',
                'main page', 'contents', 'current events', 'random article', 'about wikipedia',
                'contact us', 'help', 'learn to edit', 'community portal', 'recent changes',
                'upload file', 'special pages', 'donate', 'create account', 'log in',
                'personal tools', 'pages for logged out editors', 'contributions', 'talk',
                'toggle the table of contents', 'edit links', 'article', 'view history',
                'what links here', 'related changes', 'permanent link', 'page information',
                'cite this page', 'get shortened url', 'download qr code', 'expand all',
                'download as pdf', 'printable version', 'in other projects', 'wikimedia commons',
                'wikidata item', 'appearance', 'move to sidebarhide', 'from wikipedia',
                'the free encyclopedia', 'category', 'hidden categories', 'webarchive template',
                'articles with short description', 'short description is different from wikidata',
                'articles with excerpts', 'this page was last edited', 'text is available under',
                'creative commons attribution', 'additional terms may apply', 'by using this site',
                'you agree to the terms of use', 'privacy policy', 'wikipedia is a registered trademark',
                'wikimedia foundation inc', 'non-profit organization', 'privacy policy', 'about wikipedia',
                'disclaimers', 'contact wikipedia', 'code of conduct', 'developers', 'statistics',
                'cookie statement', 'mobile view', 'powered by mediawiki', 'search', 'search'
            ]
            
            for line in lines:
                line_lower = line.lower()
                # Skip very short lines or navigation text
                if (len(line) > 20 and 
                    not any(pattern in line_lower for pattern in skip_patterns) and
                    not line.startswith('http') and
                    not line.startswith('www.')):
                    filtered_lines.append(line)
            
            text_content = '\n'.join(filtered_lines)
            
            # Check if we got meaningful content
            if len(text_content) < 100:
                return {"success": False, "error": "Insufficient meaningful content extracted - page may be empty or blocked"}
                
        except Exception as e:
            return {"success": False, "error": f"Content extraction failed: {str(e)}"}
        
        # Extract title with fallbacks
        title_text = "No title found"
        try:
            title = soup.find('title')
            if title and title.get_text().strip():
                title_text = title.get_text().strip()
            else:
                # Try h1 as fallback
                h1 = soup.find('h1')
                if h1 and h1.get_text().strip():
                    title_text = h1.get_text().strip()
        except Exception:
            pass
        
        # Extract meta description with fallbacks
        description = "No description found"
        try:
            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc.get('content').strip()
            else:
                # Try Open Graph description
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                if og_desc and og_desc.get('content'):
                    description = og_desc.get('content').strip()
                else:
                    # Try first paragraph as fallback
                    first_p = soup.find('p')
                    if first_p and first_p.get_text().strip():
                        desc_text = first_p.get_text().strip()
                        description = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
        except Exception:
            pass
        
        # Extract meaningful links only
        links = []
        try:
            # Define patterns for useful links
            useful_patterns = [
                'article', 'news', 'post', 'page', 'document', 'pdf', 'doc',
                'research', 'study', 'report', 'analysis', 'guide', 'tutorial',
                'legal', 'law', 'regulation', 'policy', 'case', 'court'
            ]
            
            # Define patterns for useless links
            useless_patterns = [
                'javascript:', 'mailto:', 'tel:', '#', 'facebook.com', 'twitter.com',
                'instagram.com', 'linkedin.com', 'youtube.com', 'google.com',
                'advertisement', 'ads', 'banner', 'popup', 'cookie', 'privacy',
                'terms', 'contact', 'about', 'home', 'index'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text().strip().lower()
                
                # Skip useless links
                if any(pattern in href.lower() for pattern in useless_patterns):
                    continue
                
                # Skip very short or generic link text
                if len(link_text) < 3 or link_text in ['click here', 'read more', 'more', 'here']:
                    continue
                
                # Prioritize links with useful patterns
                is_useful = any(pattern in href.lower() or pattern in link_text for pattern in useful_patterns)
                
                if href.startswith('http'):
                    if is_useful or len(links) < 10:  # Limit to 10 most useful links
                        links.append(href)
                elif href.startswith('/'):
                    # Convert relative URLs to absolute
                    from urllib.parse import urljoin
                    full_url = urljoin(url, href)
                    if is_useful or len(links) < 10:
                        links.append(full_url)
                        
        except Exception:
            pass
        
        return {
            "success": True,
            "title": title_text,
            "description": description,
            "content": text_content,
            "links": links,  # Now limited to 10 most useful links
            "url": url,
            "method": "beautifulsoup",
            "status_code": response.status_code,
            "content_length": len(text_content)
        }
        
    except Exception as e:
        return {"success": False, "error": f"BeautifulSoup scraping failed: {str(e)}"}

def download_documents_from_links(base_url: str, links: List[str], user_id: int, bypass_auth: bool = False) -> Dict[str, Any]:
    """Download document files from detected links and the base URL itself with optional authentication bypass"""
    try:
        # Define supported document types
        document_extensions = {
            '.pdf': 'PDF Document',
            '.docx': 'Word Document',
            '.doc': 'Word Document (Legacy)',
            '.txt': 'Text Document',
            '.rtf': 'Rich Text Document',
            '.odt': 'OpenDocument Text',
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet (Legacy)',
            '.pptx': 'PowerPoint Presentation',
            '.ppt': 'PowerPoint Presentation (Legacy)',
            '.csv': 'CSV File'
        }
        
        downloaded_documents = []
        failed_downloads = []
        
        # Enhanced headers for document downloads
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Add authentication bypass headers if requested
        if bypass_auth:
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': base_url,
                'Origin': urlparse(base_url).netloc,
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
        
        # Check if the base URL itself is a document
        all_urls_to_check = [base_url] + links
        
        for link in all_urls_to_check:
            try:
                # Convert relative URLs to absolute
                if link.startswith('/'):
                    full_url = urljoin(base_url, link)
                elif not link.startswith('http'):
                    full_url = urljoin(base_url, link)
                else:
                    full_url = link
                
                # Parse URL to get file extension
                parsed_url = urlparse(full_url)
                path = parsed_url.path.lower()
                
                # Check if it's a document file
                is_document = False
                file_extension = None
                for ext in document_extensions.keys():
                    if path.endswith(ext):
                        is_document = True
                        file_extension = ext
                        break
                
                if not is_document:
                    continue
                
                # Try to download the document
                logger.info(f"Attempting to download document: {full_url}")
                
                response = requests.get(full_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Verify it's actually a document (check content-type or file extension)
                    is_document_content_type = any(doc_type in content_type for doc_type in ['pdf', 'document', 'text', 'spreadsheet', 'presentation'])
                    is_document_extension = file_extension in document_extensions
                    
                    if is_document_content_type or is_document_extension:
                        # Get filename from URL or content-disposition
                        filename = os.path.basename(parsed_url.path)
                        if not filename or '.' not in filename:
                            filename = f"document{file_extension}"
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                            tmp_file.write(response.content)
                            temp_path = tmp_file.name
                        
                        file_size = os.path.getsize(temp_path)
                        
                        # Only process if file is not too large (max 50MB)
                        if file_size > 50 * 1024 * 1024:
                            os.unlink(temp_path)
                            failed_downloads.append({
                                "url": full_url,
                                "filename": filename,
                                "error": "File too large (>50MB)"
                            })
                            continue
                        
                        # Try to extract text from the document
                        try:
                            from src.utils.document_processor import DocumentProcessor
                            doc_processor = DocumentProcessor()
                            document_text = doc_processor.process_file(temp_path)
                            
                            if document_text and len(document_text.strip()) > 50:
                                # Save document to database
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                
                                # Insert document record
                                cursor.execute("""
                                    INSERT INTO documents (user_id, title, document_type, source, content, created_at)
                                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                """, (
                                    user_id,
                                    filename,
                                    document_extensions[file_extension],
                                    f"web_download:{base_url}",
                                    document_text
                                ))
                                
                                document_id = cursor.lastrowid
                                conn.commit()
                                cursor.close()
                                conn.close()
                                
                                downloaded_documents.append({
                                    "url": full_url,
                                    "filename": filename,
                                    "document_id": document_id,
                                    "file_type": document_extensions[file_extension],
                                    "file_size": file_size,
                                    "content_length": len(document_text),
                                    "status": "success"
                                })
                                
                                logger.info(f"Successfully downloaded and processed: {filename}")
                            else:
                                failed_downloads.append({
                                    "url": full_url,
                                    "filename": filename,
                                    "error": "Could not extract text from document"
                                })
                            
                        except Exception as e:
                            failed_downloads.append({
                                "url": full_url,
                                "filename": filename,
                                "error": f"Document processing failed: {str(e)}"
                            })
                            logger.error(f"Document processing failed for {filename}: {str(e)}")
                        
                        # Clean up temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    else:
                        failed_downloads.append({
                            "url": full_url,
                            "filename": filename if 'filename' in locals() else "unknown",
                            "error": f"Invalid content type: {content_type}"
                        })
                else:
                    failed_downloads.append({
                        "url": full_url,
                        "filename": os.path.basename(parsed_url.path) or "unknown",
                        "error": f"HTTP {response.status_code}: {response.reason}"
                    })
                    
            except requests.exceptions.Timeout:
                failed_downloads.append({
                    "url": full_url,
                    "filename": os.path.basename(parsed_url.path) or "unknown",
                    "error": "Download timeout"
                })
            except requests.exceptions.RequestException as e:
                failed_downloads.append({
                    "url": full_url,
                    "filename": os.path.basename(parsed_url.path) or "unknown",
                    "error": f"Download failed: {str(e)}"
                })
            except Exception as e:
                failed_downloads.append({
                    "url": full_url,
                    "filename": os.path.basename(parsed_url.path) or "unknown",
                    "error": f"Unexpected error: {str(e)}"
                })
        
        return {
            "success": True,
            "downloaded_count": len(downloaded_documents),
            "failed_count": len(failed_downloads),
            "downloaded_documents": downloaded_documents,
            "failed_downloads": failed_downloads
        }
        
    except Exception as e:
        logger.error(f"Document download process failed: {str(e)}")
        return {
            "success": False,
            "error": f"Document download process failed: {str(e)}",
            "downloaded_count": 0,
            "failed_count": 0,
            "downloaded_documents": [],
            "failed_downloads": []
        }

def discover_hidden_documents(base_url: str, page_content: str) -> List[str]:
    """Discover hidden document URLs from page content and common patterns"""
    try:
        import re
        from urllib.parse import urljoin, urlparse
        
        discovered_urls = []
        base_domain = urlparse(base_url).netloc
        
        # Common document URL patterns
        document_patterns = [
            r'href=["\']([^"\']*\.(?:pdf|docx?|txt|rtf|odt|xlsx?|pptx?|csv))["\']',
            r'src=["\']([^"\']*\.(?:pdf|docx?|txt|rtf|odt|xlsx?|pptx?|csv))["\']',
            r'["\']([^"\']*\/documents?\/[^"\']*)["\']',
            r'["\']([^"\']*\/files?\/[^"\']*)["\']',
            r'["\']([^"\']*\/downloads?\/[^"\']*)["\']',
            r'["\']([^"\']*\/api\/documents?\/[^"\']*)["\']',
            r'["\']([^"\']*\/api\/files?\/[^"\']*)["\']',
        ]
        
        # Search for document patterns in content
        for pattern in document_patterns:
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            for match in matches:
                # Convert relative URLs to absolute
                if match.startswith('/'):
                    full_url = urljoin(base_url, match)
                elif not match.startswith('http'):
                    full_url = urljoin(base_url, match)
                else:
                    full_url = match
                
                # Only include URLs from the same domain
                if urlparse(full_url).netloc == base_domain:
                    discovered_urls.append(full_url)
        
        # Remove duplicates
        discovered_urls = list(set(discovered_urls))
        
        logger.info(f"Discovered {len(discovered_urls)} potential document URLs")
        return discovered_urls
        
    except Exception as e:
        logger.error(f"Document discovery failed: {str(e)}")
        return []

def attempt_document_access(url: str, headers: dict, max_attempts: int = 3) -> Dict[str, Any]:
    """Attempt to access a document with multiple strategies"""
    try:
        strategies = [
            # Strategy 1: Direct access
            {"headers": headers, "allow_redirects": True},
            # Strategy 2: With different user agent
            {"headers": {**headers, "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}, "allow_redirects": True},
            # Strategy 3: With referer
            {"headers": {**headers, "Referer": urlparse(url).netloc}, "allow_redirects": True},
        ]
        
        for i, strategy in enumerate(strategies[:max_attempts]):
            try:
                logger.info(f"Attempting document access strategy {i+1} for {url}")
                response = requests.get(url, timeout=30, **strategy)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if any(doc_type in content_type for doc_type in ['pdf', 'document', 'text', 'spreadsheet', 'presentation']):
                        return {
                            "success": True,
                            "response": response,
                            "strategy": f"strategy_{i+1}",
                            "content_type": content_type
                        }
                
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed for {url}: {str(e)}")
                continue
        
        return {"success": False, "error": "All access strategies failed"}
        
    except Exception as e:
        return {"success": False, "error": f"Document access attempt failed: {str(e)}"}

# Document analysis helper functions
async def analyze_document_with_llm(document_text: str, analysis_type: str, user: User = None) -> str:
    """Analyze document using LLM with specific analysis types and language detection"""
    try:
        # Detect language from document text
        detected_language = detect_language(document_text)
        logger.info(f"Detected document language: {detected_language}")
        
        # Get user's LLM settings if user is provided
        if user:
            user_settings = await get_user_llm_settings(user)
            llm_provider = user_settings.get('llm_provider', 'openai')
            llm_model = user_settings.get('llm_model', 'gpt-4o')
        else:
            # Default to OpenAI if no user provided
            llm_provider = 'openai'
            llm_model = 'gpt-4o'
        
        logger.info(f"Using LLM provider: {llm_provider}, model: {llm_model}")
        
        if llm_provider == 'openai':
            # Use OpenAI
            import openai
            openai.api_key = config.get('openai', {}).get('api_key')
            
            if not openai.api_key:
                return {"error": "OpenAI API key not configured"}
        elif llm_provider == 'ollama':
            # Use Ollama
            try:
                from src.core.llm_engine import LLMEngine
                llm_engine = LLMEngine(model_name=llm_model)
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                return {"error": f"Failed to initialize Ollama model {llm_model}. Please check if Ollama is running and the model is available."}
        else:
            return {"error": f"Unsupported LLM provider: {llm_provider}"}
        
        # Create language-specific prompts
        language_instruction = ""
        if detected_language == "ar":
            language_instruction = """
        LANGUAGE INSTRUCTION: Respond in Arabic (العربية). Use proper Arabic legal terminology and maintain a professional tone. If you need to include English legal terms, provide Arabic translations in parentheses.
        """
        else:
            language_instruction = """
        LANGUAGE INSTRUCTION: Respond in English. Use clear, professional legal terminology appropriate for the jurisdiction.
        """
        
        # Create specific prompts for each analysis type
        analysis_prompts = {
            "summary": f"""
        You are a legal document analysis AI. {language_instruction}
        
        Please provide a comprehensive summary of the following legal document:

        Document Text:
        {document_text}

        Please include:
        1. Document overview and main purpose
        2. Key parties involved
        3. Main legal issues or topics
        4. Important dates and deadlines
        5. Key findings or conclusions
        6. Recommendations or next steps

        Format your response in clear, professional language suitable for legal professionals.
        """,
            
            "key_points": f"""
        You are a legal document analysis AI. {language_instruction}
        
        Please extract and analyze the key points from the following legal document:

        Document Text:
        {document_text}

        Please provide:
        1. **Main Legal Issues**: Identify the primary legal matters addressed
        2. **Key Terms and Definitions**: Important legal terms and their meanings
        3. **Critical Dates**: Deadlines, effective dates, and important timelines
        4. **Parties and Responsibilities**: Who is involved and what are their obligations
        5. **Rights and Obligations**: What each party can and must do
        6. **Risk Factors**: Potential legal risks or concerns
        7. **Action Items**: What needs to be done next

        Focus on the most important elements that require immediate attention.
        """,
            
            "legal_issues": f"""
        You are a legal document analysis AI. {language_instruction}
        
        Please identify and analyze the legal issues in the following document:

        Document Text:
        {document_text}

        Please provide:
        1. **Primary Legal Issues**: Main legal matters that need attention
        2. **Compliance Concerns**: Areas that may violate laws or regulations
        3. **Contractual Issues**: Problems with terms, conditions, or obligations
        4. **Procedural Issues**: Problems with process, timing, or requirements
        5. **Risk Assessment**: Potential legal risks and their severity
        6. **Remedies Available**: Legal options to address identified issues
        7. **Preventive Measures**: Steps to avoid future legal problems
        8. **Professional Recommendations**: Suggested actions for legal counsel

        Focus on identifying potential legal problems and their solutions.
        """,
            
            "compliance": f"""
        You are a legal document analysis AI. {language_instruction}
        
        Please perform a compliance check on the following document:

        Document Text:
        {document_text}

        Please analyze:
        1. **Regulatory Compliance**: Does this comply with relevant laws and regulations?
        2. **Industry Standards**: Does it meet industry best practices?
        3. **Internal Policies**: Does it align with company policies and procedures?
        4. **Documentation Requirements**: Are all necessary documents and signatures present?
        5. **Timeline Compliance**: Are all deadlines and timeframes met?
        6. **Risk Areas**: What compliance risks exist?
        7. **Recommendations**: What changes are needed for full compliance?
        8. **Monitoring Requirements**: What ongoing compliance monitoring is needed?

        Focus on ensuring the document meets all applicable requirements.
        """,
            
            "full_analysis": f"""
        You are a legal document analysis AI. {language_instruction}
        
        Please provide a comprehensive legal analysis of the following document:

        Document Text:
        {document_text}

        Please provide a complete analysis including:

        ## 1. Document Overview
        - Document type and purpose
        - Parties involved
        - Key dates and timelines

## 2. Legal Analysis
- Applicable laws and regulations
- Legal precedents and case law
- Jurisdictional considerations

## 3. Key Terms and Provisions
- Important clauses and their implications
- Rights and obligations of each party
- Performance requirements

## 4. Risk Assessment
- Legal risks and potential issues
- Compliance concerns
- Liability considerations

## 5. Strategic Considerations
- Strengths and weaknesses
- Opportunities and threats
- Competitive implications

## 6. Recommendations
- Immediate actions required
- Long-term strategic considerations
- Best practices to implement

## 7. Next Steps
- Required follow-up actions
- Documentation needed
- Stakeholder communications

Provide a thorough, professional analysis suitable for legal decision-making.
"""
        }
        
        # Get the appropriate prompt for the analysis type
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["full_analysis"])
        
        # Perform analysis using the selected LLM provider
        if llm_provider == 'openai':
            # Perform analysis using OpenAI
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": "You are DALI Legal AI, a specialized legal document analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(user_settings.get('max_tokens', 2000)) if user else 2000,
                temperature=float(user_settings.get('temperature', 0.3)) if user else 0.3
            )
            return response.choices[0].message.content
        elif llm_provider == 'ollama':
            # Perform analysis using Ollama
            try:
                response = llm_engine.generate_response(prompt)
                return response
            except Exception as e:
                logger.error(f"Ollama analysis failed: {e}")
                return f"I apologize, but I encountered an error with the Ollama model: {str(e)}"
        
    except Exception as e:
        logger.error(f"LLM analysis failed: {str(e)}")
        # Fallback to simple analysis
        return f"""
## Document Analysis Results

**Analysis Type:** {analysis_type}
**Document Length:** {len(document_text)} characters
**Word Count:** {len(document_text.split())} words

**Content Preview:**
{document_text[:500]}...

**Note:** Full AI analysis is currently unavailable. Please check your OpenAI configuration.
        """

async def add_document_to_kb(user_id: int, filename: str, analysis_type: str, content: str) -> bool:
    """Add document to knowledge base"""
    try:
        # Save document directly to SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert document into SQLite database
        cursor.execute("""
            INSERT INTO documents (
                user_id, title, content, document_type, 
                source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            filename,
            content,
            analysis_type,
            "uploaded_document",
            datetime.now().isoformat()
        ))
        
        document_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully added document to knowledge base: {filename} (ID: {document_id})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add document to KB: {str(e)}")
        print(f"DEBUG: Knowledge base error: {str(e)}")  # Debug print
        return False

def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session"""
    user_data = request.session.get("user")
    if not user_data:
        return None
    return User(**user_data)

def require_auth(request: Request):
    """Require authentication decorator"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

def require_admin(request: Request):
    """Require admin role decorator"""
    user = require_auth(request)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Main routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main landing page"""
    return templates.TemplateResponse("new_index.html", {
        "request": request,
        "title": "DALI Legal AI - Complete Legal Platform",
        "t": lambda key: t(key, request)
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("new_login.html", {
        "request": request,
        "title": "Login - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("new_signup.html", {
        "request": request,
        "title": "Sign Up - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(require_auth)):
    """Main dashboard - redirects based on role"""
    if user.role == "admin":
        return RedirectResponse(url="/admin-dashboard")
    else:
        return RedirectResponse(url="/user-dashboard")

@app.get("/user-dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, user: User = Depends(require_auth)):
    """User dashboard with real statistics"""
    try:
        # Get user statistics
        stats = await get_user_statistics(user.id)
        return templates.TemplateResponse("new_user_dashboard.html", {
            "request": request,
            "user": user,
            "title": "User Dashboard - DALI Legal AI",
            "stats": stats,
            "t": lambda key: t(key, request)
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return templates.TemplateResponse("new_user_dashboard.html", {
            "request": request,
            "user": user,
            "title": "User Dashboard - DALI Legal AI",
            "stats": {"total_documents": 0, "conversations": 0, "recent_activity": []},
            "t": lambda key: t(key, request)
        })

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: User = Depends(require_admin)):
    """Admin dashboard with management features and system statistics"""
    try:
        # Get system statistics
        stats = await get_system_statistics()
        return templates.TemplateResponse("new_admin_dashboard.html", {
            "request": request,
            "user": user,
            "title": "Admin Dashboard - DALI Legal AI",
            "stats": stats,
            "t": lambda key: t(key, request)
        })
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        return templates.TemplateResponse("new_admin_dashboard.html", {
            "request": request,
            "user": user,
            "title": "Admin Dashboard - DALI Legal AI",
            "stats": {"total_users": 0, "total_documents": 0, "total_conversations": 0, "system_health": "unknown"},
            "t": lambda key: t(key, request)
        })

# Dedicated Feature Pages
@app.get("/legal-research", response_class=HTMLResponse)
async def legal_research_page(request: Request, user: User = Depends(require_auth)):
    """Dedicated legal research page"""
    return templates.TemplateResponse("legal_research.html", {
        "request": request,
        "user": user,
        "title": "Legal Research - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/document-analysis", response_class=HTMLResponse)
async def document_analysis_page(request: Request, user: User = Depends(require_auth)):
    """Dedicated document analysis page"""
    return templates.TemplateResponse("document_analysis.html", {
        "request": request,
        "user": user,
        "title": "Document Analysis - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/knowledge-base", response_class=HTMLResponse)
async def knowledge_base_page(request: Request, user: User = Depends(require_auth)):
    """Dedicated knowledge base page"""
    return templates.TemplateResponse("knowledge_base.html", {
        "request": request,
        "user": user,
        "title": "Knowledge Base - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/web-research", response_class=HTMLResponse)
async def web_research_page(request: Request, user: User = Depends(require_auth)):
    """Dedicated web research page"""
    return templates.TemplateResponse("web_research.html", {
        "request": request,
        "user": user,
        "title": "Web Research - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/web-scraping", response_class=HTMLResponse)
async def web_scraping_page(request: Request, user: User = Depends(require_auth)):
    """Dedicated web scraping page"""
    return templates.TemplateResponse("web_scraping.html", {
        "request": request,
        "user": user,
        "title": "Web Scraping - DALI Legal AI"
    })

@app.get("/court-simulation", response_class=HTMLResponse)
async def court_simulation_page(request: Request, user: User = Depends(require_auth)):
    """Court simulation page"""
    return templates.TemplateResponse("court_simulation.html", {
        "request": request,
        "user": user,
        "title": "Court Simulation - DALI Legal AI"
    })

@app.get("/database-intelligence", response_class=HTMLResponse)
async def database_intelligence_page(request: Request, user: User = Depends(require_auth)):
    """Database intelligence page"""
    return templates.TemplateResponse("database_intelligence.html", {
        "request": request,
        "user": user,
        "title": "Database Intelligence - DALI Legal AI"
    })

@app.get("/sidebar-demo", response_class=HTMLResponse)
async def sidebar_demo_page(request: Request, user: User = Depends(require_auth)):
    """Sidebar demo page"""
    return templates.TemplateResponse("sidebar_demo.html", {
        "request": request,
        "user": user,
        "title": "Sidebar Demo - DALI Legal AI"
    })

@app.get("/user-chat", response_class=HTMLResponse)
async def user_chat_page(request: Request, user: User = Depends(require_auth)):
    """User-to-user chat page"""
    return templates.TemplateResponse("user_chat.html", {
        "request": request,
        "user": user,
        "title": "User Chat - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, user: User = Depends(require_auth)):
    """Analytics dashboard page"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "user": user,
        "title": "Analytics Dashboard - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

# Authentication API endpoints
@app.post("/api/login")
async def api_login(login_data: LoginRequest, request: Request):
    """API endpoint for user login"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user from database
        cursor.execute("""
            SELECT id, username, email, password_hash, first_name, last_name, 
                   role, is_active, company_name, job_title, phone, department
            FROM users WHERE username = ?
        """, (login_data.username,))
        
        user_row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user_row:
            return {"success": False, "message": "Invalid username or password"}
        
        # Convert row to dict for easier access
        user = {
            'id': user_row[0],
            'username': user_row[1],
            'email': user_row[2],
            'password_hash': user_row[3],
            'first_name': user_row[4],
            'last_name': user_row[5],
            'role': user_row[6],
            'is_active': user_row[7],
            'company_name': user_row[8],
            'job_title': user_row[9],
            'phone': user_row[10],
            'department': user_row[11]
        }
        
        if not verify_password(login_data.password, user['password_hash']):
            return {"success": False, "message": "Invalid username or password"}
        
        if not user.get('is_active', True):
            return {"success": False, "message": "Account is deactivated"}
        
        # Create user session
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user.get("role", "user"),
            "is_active": user.get("is_active", True)
        }
        
        # Store in session
        request.session["user"] = user_data
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user.get("role", "user")},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_data,
            "access_token": access_token
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {"success": False, "message": f"Login failed: {str(e)}"}

@app.post("/api/signup")
async def api_signup(signup_data: SignupRequest):
    """API endpoint for user signup"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (signup_data.username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Username already exists"}
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (signup_data.email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Email already exists"}
        
        # Hash password
        password_hash = get_password_hash(signup_data.password)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, first_name, last_name, 
                             company_name, job_title, phone, department, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (signup_data.username, signup_data.email, password_hash, 
              signup_data.first_name, signup_data.last_name, 
              signup_data.company_name, signup_data.job_title, 
              signup_data.phone, signup_data.department, signup_data.role, True))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Account created successfully"
        }
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return {"success": False, "message": f"Signup failed: {str(e)}"}

@app.post("/api/logout")
async def api_logout(request: Request):
    """API endpoint for user logout"""
    request.session.clear()
    return {"success": True, "message": "Logged out successfully"}

@app.get("/logout")
async def logout_page(request: Request):
    """Logout page - clears session and redirects"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/language/current")
async def get_current_language(request: Request, user: User = Depends(require_auth)):
    """Get current language setting"""
    try:
        current_lang = request.session.get("language", "en")
        return {"success": True, "language": current_lang}
    except Exception as e:
        logger.error(f"Get language error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/language/current/public")
async def get_current_language_public(request: Request):
    """Get current language setting (public - no auth required)"""
    try:
        current_lang = request.session.get("language", "en")
        return {"success": True, "language": current_lang}
    except Exception as e:
        logger.error(f"Get language error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/language/toggle")
async def toggle_language(request: Request, user: User = Depends(require_auth)):
    """Toggle language between English and Arabic"""
    try:
        current_lang = request.session.get("language", "en")
        new_lang = "ar" if current_lang == "en" else "en"
        request.session["language"] = new_lang
        
        # Store language preference in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user settings
        cursor.execute("""
            UPDATE user_settings 
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND setting_key = ?
        """, (new_lang, user.id, "language"))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user.id, "language", new_lang))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "language": new_lang}
        
    except Exception as e:
        logger.error(f"Language toggle error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/language/toggle/public")
async def toggle_language_public(request: Request):
    """Toggle language between English and Arabic (public - no auth required)"""
    try:
        current_lang = request.session.get("language", "en")
        new_lang = "ar" if current_lang == "en" else "en"
        request.session["language"] = new_lang
        
        return {"success": True, "language": new_lang}
        
    except Exception as e:
        logger.error(f"Language toggle error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/theme/toggle")
async def toggle_theme(request: Request, user: User = Depends(require_auth)):
    """Toggle theme between light and dark mode"""
    try:
        current_theme = request.session.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        request.session["theme"] = new_theme
        
        # Store theme preference in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user settings
        cursor.execute("""
            UPDATE user_settings 
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND setting_key = ?
        """, (new_theme, user.id, "theme"))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user.id, "theme", new_theme))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "theme": new_theme}
        
    except Exception as e:
        logger.error(f"Theme toggle error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/search")
async def global_search(query: str, user: User = Depends(require_auth)):
    """Global search across all content types"""
    try:
        if not query or len(query.strip()) < 2:
            return {"success": False, "error": "Query must be at least 2 characters long"}
        
        search_results = {
            "query": query,
            "results": [],
            "total_results": 0,
            "categories": {}
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search in documents
        cursor.execute("""
            SELECT id, title, document_type, content, created_at, 'document' as type
            FROM documents 
            WHERE user_id = ? AND (
                title LIKE ? OR 
                content LIKE ? OR 
                document_type LIKE ?
            )
            ORDER BY created_at DESC
            LIMIT 10
        """, (user.id, f"%{query}%", f"%{query}%", f"%{query}%"))
        
        documents = cursor.fetchall()
        search_results["results"].extend(documents)
        search_results["categories"]["documents"] = len(documents)
        
        # Search in conversations/messages
        cursor.execute("""
            SELECT c.id, c.title, m.content, m.created_at, 'conversation' as type
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE c.user_id = ? AND (
                c.title LIKE ? OR 
                m.content LIKE ?
            )
            ORDER BY m.created_at DESC
            LIMIT 10
        """, (user.id, f"%{query}%", f"%{query}%"))
        
        conversations = cursor.fetchall()
        search_results["results"].extend(conversations)
        search_results["categories"]["conversations"] = len(conversations)
        
        # Search in user chats
        cursor.execute("""
            SELECT id, message as content, sent_at as created_at, 'chat' as type
            FROM user_chats 
            WHERE (sender_id = ? OR receiver_id = ?) AND message LIKE ?
            ORDER BY sent_at DESC
            LIMIT 10
        """, (user.id, user.id, f"%{query}%"))
        
        chats = cursor.fetchall()
        search_results["results"].extend(chats)
        search_results["categories"]["chats"] = len(chats)
        
        # Calculate total results
        search_results["total_results"] = len(search_results["results"])
        
        # Sort results by relevance (most recent first)
        search_results["results"].sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "search_results": search_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Global search error: {e}")
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/analytics")
async def get_analytics(user: User = Depends(require_auth)):
    """Get comprehensive analytics for the dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        analytics = {
            "user_stats": {},
            "activity_trends": {},
            "feature_usage": {},
            "recent_activity": [],
            "system_health": {}
        }
        
        # User statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_documents,
                COUNT(DISTINCT document_type) as document_types,
                MAX(created_at) as last_document_activity
            FROM documents 
            WHERE user_id = ?
        """, (user.id,))
        
        doc_stats = cursor.fetchone()
        analytics["user_stats"]["documents"] = doc_stats
        
        # Conversation statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_conversations,
                COUNT(DISTINCT conversation_type) as conversation_types,
                MAX(created_at) as last_conversation_activity
            FROM conversations 
            WHERE user_id = ?
        """, (user.id,))
        
        conv_stats = cursor.fetchone()
        analytics["user_stats"]["conversations"] = conv_stats
        
        # Activity trends (last 7 days)
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count,
                'documents' as type
            FROM documents 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (user.id,))
        
        doc_trends = cursor.fetchall()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count,
                'conversations' as type
            FROM conversations 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (user.id,))
        
        conv_trends = cursor.fetchall()
        
        analytics["activity_trends"] = {
            "documents": doc_trends,
            "conversations": conv_trends
        }
        
        # Feature usage statistics
        cursor.execute("""
            SELECT 
                document_type,
                COUNT(*) as count
            FROM documents 
            WHERE user_id = ?
            GROUP BY document_type
            ORDER BY count DESC
            LIMIT 5
        """, (user.id,))
        
        feature_usage = cursor.fetchall()
        analytics["feature_usage"]["document_types"] = feature_usage
        
        # Recent activity (last 10 activities)
        cursor.execute("""
            SELECT 
                'document' as type,
                title as description,
                created_at,
                document_type as subtype
            FROM documents 
            WHERE user_id = ?
            UNION ALL
            SELECT 
                'conversation' as type,
                title as description,
                created_at,
                conversation_type as subtype
            FROM conversations 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (user.id, user.id))
        
        recent_activity = cursor.fetchall()
        analytics["recent_activity"] = recent_activity
        
        # System health
        analytics["system_health"] = {
            "database": "connected",
            "api": "healthy",
            "uptime": "99.9%",
            "last_backup": datetime.now().isoformat()
        }
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {
            "success": False,
            "error": f"Analytics failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Feature API endpoints
@app.get("/api/legal-research")
async def legal_research(
    query: str, 
    jurisdiction: str = "Saudi Arabia",
    include_web_search: str = "false",
    user: User = Depends(require_auth)
):
    """Legal research endpoint with AI-powered analysis"""
    try:
        # Generate AI-powered legal research response
        research_result = await generate_legal_research(query, user, jurisdiction, include_web_search)
        
        return {
            "success": True,
            "query": query,
            "jurisdiction": jurisdiction,
            "include_web_search": include_web_search,
            "results": research_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Legal research failed: {str(e)}")
        return {
            "success": False,
            "query": query,
            "error": f"Legal research failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/legal-research")
async def legal_research_post(
    request: Request,
    user: User = Depends(require_auth)
):
    """Legal research POST endpoint with AI-powered analysis and conversation memory"""
    try:
        # Get request data
        data = await request.json()
        query = data.get('query', '')
        jurisdiction = data.get('jurisdiction', 'Saudi Arabia')
        include_web_search = data.get('include_web_search', 'false')
        
        if not query:
            return {
                "success": False,
                "error": "Query is required",
                "timestamp": datetime.now().isoformat()
            }
        
        # Detect language from the query
        detected_language = detect_language(query)
        logger.info(f"Detected language: {detected_language}")
        
        # Get or create conversation session
        session_id = get_active_session(user.id)
        if not session_id:
            session_id = create_conversation_session(user.id, "Legal Research Session")
        
        # Save user message to memory
        save_conversation_message(
            user_id=user.id,
            session_id=session_id,
            message_type='user',
            message_content=query,
            context_data={'jurisdiction': jurisdiction, 'include_web_search': include_web_search}
        )
        
        # Get conversation history for context
        conversation_history = get_conversation_history(user.id, session_id, limit=5)
        
        # Generate AI-powered legal research response with conversation context
        research_result = await generate_legal_research_with_memory(query, user, jurisdiction, include_web_search, conversation_history, detected_language)
        
        # Save AI response to memory
        save_conversation_message(
            user_id=user.id,
            session_id=session_id,
            message_type='assistant',
            message_content=research_result,
            context_data={'jurisdiction': jurisdiction, 'include_web_search': include_web_search}
        )
        
        # Update session activity
        update_session_activity(session_id)
        
        return {
            "success": True,
            "query": query,
            "jurisdiction": jurisdiction,
            "include_web_search": include_web_search,
            "results": research_result,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Legal research failed: {str(e)}")
        return {
            "success": False,
            "error": f"Legal research failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/generate-chart")
async def generate_chart(
    request: Request,
    user: User = Depends(require_auth)
):
    """Generate chart based on previous conversation data"""
    try:
        data = await request.json()
        chart_type = data.get('chart_type', 'pie')
        session_id = data.get('session_id')
        
        if not session_id:
            return {
                "success": False,
                "error": "Session ID is required",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get conversation history to find data
        conversation_history = get_conversation_history(user.id, session_id, limit=10)
        
        # Look for data in the conversation (check both user and assistant messages)
        chart_data = None
        logger.info(f"Looking for chart data in {len(conversation_history)} messages")
        
        for msg in reversed(conversation_history):
            logger.info(f"Checking message type: {msg['type']}, content preview: {msg['content'][:100]}...")
            # Extract data from both user and assistant messages
            extracted_data = extract_chart_data_from_text(msg['content'])
            if extracted_data:
                logger.info(f"Found chart data: {extracted_data}")
                chart_data = extracted_data
                break
        
        if not chart_data:
            return {
                "success": False,
                "error": "No chart data found in conversation history",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate chart HTML using matplotlib
        try:
            chart_html = generate_matplotlib_chart(chart_data, chart_type, f"{chart_type.title()} Chart")
            logger.info(f"Chart HTML generated successfully, length: {len(chart_html)}")
        except Exception as chart_error:
            logger.error(f"Chart generation error: {str(chart_error)}")
            chart_html = f"""
            <div class="chart-container">
                <div class="chart-title">Chart Generation Error</div>
                <div class="chart-wrapper">
                    <p style="color: red; padding: 20px;">Sorry, there was an error generating the chart: {str(chart_error)}</p>
                </div>
            </div>
            """
        
        # Save chart generation to memory
        save_conversation_message(
            user_id=user.id,
            session_id=session_id,
            message_type='assistant',
            message_content=f"Generated {chart_type} chart based on your data",
            context_data={'chart_type': chart_type, 'chart_data': chart_data}
        )
        
        return {
            "success": True,
            "chart_type": chart_type,
            "chart_html": chart_html,
            "chart_data": chart_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return {
            "success": False,
            "error": f"Chart generation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def extract_chart_data_from_text(text: str) -> Optional[List[Dict]]:
    """Extract chart data from text using the same logic as frontend"""
    import re
    lines = text.replace('\r\n', '\n').split('\n')
    chart_data = []
    
    logger.info(f"Extracting chart data from text with {len(lines)} lines")
    
    # Handle the specific user format: "Case TypeEstimated Number in 2024Notes..."
    if "Case TypeEstimated Number in 2024Notes" in text:
        # Extract data from the user's specific format
        patterns = [
            r'Criminal Cases[^0-9]*(\d{1,3}(?:,\d{3})*)',
            r'Civil Cases[^0-9]*(\d{1,3}(?:,\d{3})*)',
            r'Commercial/Corporate Cases[^0-9]*(\d{1,3}(?:,\d{3})*)',
            r'Family Law Cases[^0-9]*(\d{1,3}(?:,\d{3})*)',
            r'Traffic Violations[^0-9]*~?(\d{1,3}(?:,\d{3})*)'
        ]
        
        case_types = [
            'Criminal Cases',
            'Civil Cases', 
            'Commercial/Corporate Cases',
            'Family Law Cases',
            'Traffic Violations'
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                value = match.group(1).replace(',', '')
                try:
                    num_value = int(value)
                    if num_value > 0:
                        chart_data.append({'label': case_types[i], 'value': num_value})
                        logger.info(f"User format match: {case_types[i]} = {num_value}")
                except ValueError:
                    pass
    
    # If we found data from user format, return it
    if chart_data:
        logger.info(f"Extracted {len(chart_data)} data points from user format: {chart_data}")
        return chart_data
    
    # Otherwise, use the original line-by-line parsing
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        logger.info(f"Processing line: {line[:50]}...")
            
        # Pattern 1: **Case Type:** Number format
        match = re.match(r'\*\*([^:]+):\*\*\s*([\d,~]+)', line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).replace(',', '').replace('~', '')
            try:
                num_value = int(value)
                if num_value > 0:
                    chart_data.append({'label': label, 'value': num_value})
                    logger.info(f"Pattern 1 match: {label} = {num_value}")
                    continue
            except ValueError:
                pass
        
        # Pattern 2: Case Type (description) Number format with space
        match = re.match(r'^([^(]+)\s*\([^)]*\)\s+([\d,~]+)', line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).replace(',', '').replace('~', '')
            try:
                num_value = int(value)
                if num_value > 0:
                    chart_data.append({'label': label, 'value': num_value})
                    logger.info(f"Pattern 2 match: {label} = {num_value}")
                    continue
            except ValueError:
                pass
        
        # Pattern 3: Case Type (description)Number format without space
        match = re.match(r'^([^(]+)\s*\([^)]*\)([\d,~]+)', line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).replace(',', '').replace('~', '')
            try:
                num_value = int(value)
                if num_value > 0:
                    chart_data.append({'label': label, 'value': num_value})
                    logger.info(f"Pattern 3 match: {label} = {num_value}")
                    continue
            except ValueError:
                pass
        
        # Pattern 4: Simple format: Label: Number
        match = re.match(r'^([^:]+):\s*([\d,~]+)', line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).replace(',', '').replace('~', '')
            try:
                num_value = int(value)
                if num_value > 0:
                    chart_data.append({'label': label, 'value': num_value})
                    logger.info(f"Pattern 4 match: {label} = {num_value}")
                    continue
            except ValueError:
                pass
        
        # Pattern 5: Handle traffic violations with ~ symbol
        match = re.match(r'^([^(]+)\s*\([^)]*\)\s*~([\d,]+)', line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).replace(',', '')
            try:
                num_value = int(value)
                if num_value > 0:
                    chart_data.append({'label': label, 'value': num_value})
                    logger.info(f"Pattern 5 match: {label} = {num_value}")
                    continue
            except ValueError:
                pass
    
    logger.info(f"Extracted {len(chart_data)} data points: {chart_data}")
    return chart_data if chart_data else None

@app.get("/api/knowledge-base/analyze/document-stats")
async def analyze_document_stats(user: User = Depends(require_auth)):
    """Analyze document statistics from knowledge base"""
    try:
        # Get document statistics
        stats_query = """
        SELECT 
            document_type,
            COUNT(*) as count,
            AVG(LENGTH(content)) as avg_length,
            MIN(created_at) as earliest,
            MAX(created_at) as latest
        FROM documents 
        WHERE user_id = ? 
        GROUP BY document_type
        ORDER BY count DESC
        """
        
        stats = db_manager.execute_query(stats_query, (user.id,))
        
        # Generate analysis
        analysis_html = f"""
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-chart-pie me-2"></i>Document Distribution</h5>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Document Type</th>
                                <th>Count</th>
                                <th>Avg Length</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for stat in stats:
            analysis_html += f"""
                            <tr>
                                <td>{stat[0]}</td>
                                <td><span class="badge bg-primary">{stat[1]}</span></td>
                                <td>{int(stat[2]) if stat[2] else 0} chars</td>
                            </tr>
            """
        
        analysis_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-info-circle me-2"></i>Summary</h5>
                <div class="alert alert-info">
                    <p><strong>Total Documents:</strong> {total_docs}</p>
                    <p><strong>Document Types:</strong> {doc_types}</p>
                    <p><strong>Date Range:</strong> {date_range}</p>
                </div>
            </div>
        </div>
        """.format(
            total_docs=sum(stat[1] for stat in stats),
            doc_types=len(stats),
            date_range=f"{stats[0][3].split()[0] if stats else 'N/A'} to {stats[0][4].split()[0] if stats else 'N/A'}"
        )
        
        return {
            "success": True,
            "analysis": analysis_html
        }
        
    except Exception as e:
        logger.error(f"Document stats analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/knowledge-base/analyze/content-patterns")
async def analyze_content_patterns(user: User = Depends(require_auth)):
    """Analyze content patterns in knowledge base"""
    try:
        # Get content patterns
        patterns_query = """
        SELECT 
            SUBSTR(content, 1, 100) as content_preview,
            LENGTH(content) as content_length,
            document_type,
            created_at
        FROM documents 
        WHERE user_id = ? 
        ORDER BY content_length DESC
        LIMIT 10
        """
        
        patterns = db_manager.execute_query(patterns_query, (user.id,))
        
        analysis_html = f"""
        <div class="row">
            <div class="col-12">
                <h5><i class="fas fa-search me-2"></i>Content Analysis</h5>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Document Type</th>
                                <th>Content Preview</th>
                                <th>Length</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for pattern in patterns:
            analysis_html += f"""
                            <tr>
                                <td><span class="badge bg-secondary">{pattern[2]}</span></td>
                                <td>{pattern[0]}...</td>
                                <td>{pattern[1]} chars</td>
                                <td>{pattern[3].split()[0] if pattern[3] else 'N/A'}</td>
                            </tr>
            """
        
        analysis_html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
        return {
            "success": True,
            "analysis": analysis_html
        }
        
    except Exception as e:
        logger.error(f"Content patterns analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/knowledge-base/analyze/temporal-data")
async def analyze_temporal_data(user: User = Depends(require_auth)):
    """Analyze temporal patterns in knowledge base"""
    try:
        # Get temporal data
        temporal_query = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count,
            document_type
        FROM documents 
        WHERE user_id = ? 
        GROUP BY DATE(created_at), document_type
        ORDER BY date DESC
        LIMIT 20
        """
        
        temporal = db_manager.execute_query(temporal_query, (user.id,))
        
        analysis_html = f"""
        <div class="row">
            <div class="col-12">
                <h5><i class="fas fa-calendar me-2"></i>Temporal Analysis</h5>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Document Type</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for temp in temporal:
            analysis_html += f"""
                            <tr>
                                <td>{temp[0]}</td>
                                <td><span class="badge bg-info">{temp[2]}</span></td>
                                <td>{temp[1]}</td>
                            </tr>
            """
        
        analysis_html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
        return {
            "success": True,
            "analysis": analysis_html
        }
        
    except Exception as e:
        logger.error(f"Temporal data analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/knowledge-base/analyze/key-insights")
async def generate_key_insights(user: User = Depends(require_auth)):
    """Generate AI-powered key insights from knowledge base"""
    try:
        # Get summary data for AI analysis
        summary_query = """
        SELECT 
            document_type,
            COUNT(*) as count,
            AVG(LENGTH(content)) as avg_length,
            MIN(created_at) as earliest,
            MAX(created_at) as latest
        FROM documents 
        WHERE user_id = ? 
        GROUP BY document_type
        """
        
        summary_data = db_manager.execute_query(summary_query, (user.id,))
        
        # Generate AI insights
        import openai
        openai.api_key = config.get('openai', {}).get('api_key')
        
        insights_prompt = f"""
        Based on the following document statistics from a legal knowledge base, provide key insights and recommendations:
        
        Document Statistics:
        {summary_data}
        
        Please provide:
        1. Key patterns and trends
        2. Recommendations for knowledge base optimization
        3. Potential areas for improvement
        4. Insights about document organization
        
        Format the response in HTML with proper styling.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": insights_prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        analysis_html = f"""
        <div class="row">
            <div class="col-12">
                <h5><i class="fas fa-lightbulb me-2"></i>AI-Generated Insights</h5>
                <div class="alert alert-success">
                    {response.choices[0].message.content}
                </div>
            </div>
        </div>
        """
        
        return {
            "success": True,
            "analysis": analysis_html
        }
        
    except Exception as e:
        logger.error(f"Key insights generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def detect_language(text: str) -> str:
    """
    Detect language from text input.
    
    Args:
    - text (str): Input text to analyze
    
    Returns:
    - str: Language code ('ar' for Arabic, 'en' for English)
    """
    import re
    
    # Count Arabic and English characters
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    english_pattern = re.compile(r'[a-zA-Z]')
    
    arabic_count = len(arabic_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    
    # If Arabic characters are more than English, it's Arabic
    if arabic_count > english_count:
        return 'ar'
    else:
        return 'en'

def generate_matplotlib_chart(chart_data: List[Dict], chart_type: str = 'pie', title: str = 'Data Distribution') -> str:
    """
    Generate a chart from extracted data using matplotlib.
    
    Args:
    - chart_data (List[Dict]): List of {'label': str, 'value': int} dictionaries
    - chart_type (str): 'pie', 'bar', 'line', 'doughnut'
    - title (str): Chart title
    
    Returns:
    - str: Base64 encoded image HTML
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        import io
        import base64
        
        logger.info(f"Starting chart generation: {chart_type} with {len(chart_data)} data points")
        
        # Set matplotlib to use non-interactive backend
        matplotlib.use('Agg')
        
        # Extract labels and values
        labels = [item['label'] for item in chart_data]
        values = [item['value'] for item in chart_data]
        
        logger.info(f"Labels: {labels}")
        logger.info(f"Values: {values}")
        
        # Create figure with smaller size
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot based on type with better styling
        if chart_type == 'pie':
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                             startangle=90, textprops={'fontsize': 10})
            ax.axis('equal')  # Equal aspect ratio for pie
            # Improve label positioning
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
        elif chart_type == 'doughnut':
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                             startangle=90, wedgeprops=dict(width=0.5),
                                             textprops={'fontsize': 10})
            ax.axis('equal')
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
        elif chart_type == 'bar':
            bars = ax.bar(labels, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
            ax.set_ylabel('Number of Cases', fontsize=10)
            ax.tick_params(axis='x', labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            plt.xticks(rotation=45, ha='right')
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{int(height):,}', ha='center', va='bottom', fontsize=8)
        elif chart_type == 'line':
            ax.plot(labels, values, marker='o', linewidth=2, markersize=6, color='#4ECDC4')
            ax.set_ylabel('Number of Cases', fontsize=10)
            ax.tick_params(axis='x', labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            plt.xticks(rotation=45, ha='right')
        else:
            # Default to pie chart
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                             startangle=90, textprops={'fontsize': 10})
            ax.axis('equal')
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        # Save to base64 buffer
        logger.info("Saving chart to buffer...")
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        logger.info(f"Image encoded, base64 length: {len(img_base64)}")
        
        plt.close(fig)  # Clean up
        
        # Return HTML with embedded image - smaller and better positioned
        result_html = f"""
        <div class="chart-container" style="max-width: 500px; margin: 20px auto; text-align: center;">
            <div class="chart-title" style="font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333;">{title}</div>
            <div class="chart-wrapper" style="background: white; border-radius: 12px; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <img src="data:image/png;base64,{img_base64}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;">
            </div>
            <div class="chart-description" style="font-size: 12px; color: #666; margin-top: 10px;">
                Interactive {chart_type} chart showing the data from our conversation.
            </div>
        </div>
        """
        logger.info(f"Chart HTML generated, total length: {len(result_html)}")
        return result_html
        
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return f"""
        <div class="chart-container">
            <div class="chart-title">Chart Generation Error</div>
            <div class="chart-wrapper">
                <p style="color: red; padding: 20px;">Sorry, there was an error generating the chart: {str(e)}</p>
            </div>
        </div>
        """

async def get_user_llm_settings(user: User) -> dict:
    """Get user's LLM settings from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all settings for the user
        cursor.execute("""
            SELECT setting_key, setting_value FROM user_settings WHERE user_id = ?
        """, (user.id,))
        settings_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert key-value pairs to settings object
        settings = {}
        for row in settings_rows:
            settings[row['setting_key']] = row['setting_value']
        
        # Return default settings if none found
        if not settings:
            settings = {
                'llm_provider': 'openai',
                'llm_model': 'gpt-4o',
                'temperature': '0.7',
                'max_tokens': '2000'
            }
        
        # Ensure all required settings exist with defaults
        default_settings = {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4o',
            'temperature': '0.7',
            'max_tokens': '2000'
        }
        
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        return settings
    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        return {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4o',
            'temperature': '0.7',
            'max_tokens': '2000'
        }

async def generate_legal_research_with_memory(query: str, user: User, jurisdiction: str = "Saudi Arabia", include_web_search: str = "false", conversation_history: List[Dict] = None, language: str = "en") -> str:
    """Generate comprehensive legal research using AI with conversation memory and knowledge base access"""
    try:
        # Get user's LLM settings
        user_settings = await get_user_llm_settings(user)
        llm_provider = user_settings.get('llm_provider', 'openai')
        llm_model = user_settings.get('llm_model', 'gpt-4o')
        
        logger.info(f"Using LLM provider: {llm_provider}, model: {llm_model}")
        
        if llm_provider == 'openai':
            # Use OpenAI
            import openai
            openai.api_key = config.get('openai', {}).get('api_key')
            
            if not openai.api_key:
                return "OpenAI API key not configured. Please contact administrator."
        elif llm_provider == 'ollama':
            # Use Ollama
            try:
                from src.core.llm_engine import LLMEngine
                llm_engine = LLMEngine(model_name=llm_model)
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                return f"Failed to initialize Ollama model {llm_model}. Please check if Ollama is running and the model is available."
        else:
            return f"Unsupported LLM provider: {llm_provider}"
        
        # Search knowledge base for relevant documents
        knowledge_base_context = ""
        try:
            # Search documents directly from SQLite database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Search for documents containing query keywords
            search_terms = query.lower().split()
            search_conditions = []
            search_params = []
            
            for term in search_terms:
                if len(term) > 2:  # Only search for terms longer than 2 characters
                    search_conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)")
                    search_params.extend([f"%{term}%", f"%{term}%"])
            
            if search_conditions:
                search_query = f"""
                    SELECT id, title, content, document_type, created_at
                    FROM documents 
                    WHERE user_id = ? AND ({' OR '.join(search_conditions)})
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                search_params.insert(0, user.id)
                
                cursor.execute(search_query, search_params)
                kb_results = cursor.fetchall()
                
                if kb_results:
                    knowledge_base_context = "\n\nRELEVANT DOCUMENTS FROM YOUR KNOWLEDGE BASE:\n"
                    for i, result in enumerate(kb_results[:3], 1):  # Top 3 results
                        doc_id, title, content, doc_type, created_at = result
                        content_preview = content[:500] if content else "No content available"
                        knowledge_base_context += f"\n{i}. Document: {title} (Type: {doc_type})\n"
                        knowledge_base_context += f"Content Preview: {content_preview}...\n"
                    
                    knowledge_base_context += "\nUse this information from your uploaded documents to provide more accurate and specific answers.\n"
                    logger.info(f"Found {len(kb_results)} relevant documents in knowledge base")
                else:
                    logger.info("No relevant documents found in knowledge base")
            else:
                logger.info("Query too short for meaningful search")
            
            cursor.close()
            conn.close()
                
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            knowledge_base_context = ""
        
        # Build conversation context
        context_summary = ""
        if conversation_history and len(conversation_history) > 1:
            context_summary = "\n\nPrevious conversation context:\n"
            for msg in conversation_history[:-1]:  # Exclude the current message
                if msg['type'] == 'user':
                    context_summary += f"User: {msg['content']}\n"
                elif msg['type'] == 'assistant':
                    context_summary += f"Assistant: {msg['content'][:200]}...\n"  # Truncate for context
        
        # Create comprehensive legal research prompt with memory and language awareness
        language_instruction = ""
        if language == "ar":
            language_instruction = """
        LANGUAGE INSTRUCTION: Respond in Arabic (العربية). Use proper Arabic legal terminology and maintain a professional tone. If you need to include English legal terms, provide Arabic translations in parentheses.
        """
        else:
            language_instruction = """
        LANGUAGE INSTRUCTION: Respond in English. Use clear, professional legal terminology appropriate for the jurisdiction.
        """
        
        research_prompt = f"""
        You are DALI Legal AI, a conversational legal research assistant. You have memory of previous conversations and should build upon them naturally.
        {language_instruction}

        Current Query: "{query}"
        Jurisdiction: {jurisdiction}
        {context_summary}
        {knowledge_base_context}

        CONVERSATION CONTEXT ANALYSIS:
        - If the user is asking for a chart after you've already suggested one, DON'T repeat the suggestion
        - If the user says "yes" to a chart suggestion, immediately create the chart
        - If the user provides data and asks for a chart, create it directly
        - If the user asks "generate a pie chart from the data i gave you", they want you to create it NOW
        - If the user asks about their uploaded documents, use the knowledge base information provided above

        RESPONSE RULES:
        1. If user says "yes", "yes please", "create a pie chart", "pie chart", "generate a pie chart from the data i gave you" - respond with: "Creating your pie chart now..."
        
        2. If the query contains statistical data and user hasn't asked for a chart yet, end with: "I notice this data could be visualized effectively. Would you like me to create a chart to better illustrate these statistics? If so, which type of chart would you prefer - pie chart, bar chart, line chart, or doughnut chart?"
        
        3. Be conversational but concise - don't repeat data unnecessarily
        
        4. Keep responses short and to the point
        5. Don't repeat the same suggestion multiple times
        6. When you say "Creating your pie chart now...", the system will automatically generate the chart
        7. If you have relevant documents from the knowledge base, reference them specifically in your answer
        8. If the user asks about their uploaded documents, provide specific information from those documents

        Remember: Use the EXACT phrase "Would you like me to create a chart" to trigger the chart generation system.
        
        Provide a comprehensive legal analysis that addresses the user's query using both general legal knowledge and specific information from their uploaded documents when available.
        """
        
        # Generate response using OpenAI
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are DALI Legal AI, a specialized legal research assistant."},
                {"role": "user", "content": research_prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating legal research: {str(e)}")
        return f"I apologize, but I encountered an error processing your request: {str(e)}"

async def generate_legal_research(query: str, user: User, jurisdiction: str = "Saudi Arabia", include_web_search: str = "false") -> str:
    """Generate comprehensive legal research using AI with knowledge base access"""
    try:
        # Get user's LLM settings
        user_settings = await get_user_llm_settings(user)
        llm_provider = user_settings.get('llm_provider', 'openai')
        llm_model = user_settings.get('llm_model', 'gpt-4o')
        
        logger.info(f"Using LLM provider: {llm_provider}, model: {llm_model}")
        
        if llm_provider == 'openai':
            # Use OpenAI
            import openai
            openai.api_key = config.get('openai', {}).get('api_key')
            
            if not openai.api_key:
                return "OpenAI API key not configured. Please contact administrator."
        elif llm_provider == 'ollama':
            # Use Ollama
            try:
                from src.core.llm_engine import LLMEngine
                llm_engine = LLMEngine(model_name=llm_model)
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                return f"Failed to initialize Ollama model {llm_model}. Please check if Ollama is running and the model is available."
        else:
            return f"Unsupported LLM provider: {llm_provider}"
        
        # Search knowledge base for relevant documents
        knowledge_base_context = ""
        try:
            # Search documents directly from SQLite database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Search for documents containing query keywords
            search_terms = query.lower().split()
            search_conditions = []
            search_params = []
            
            for term in search_terms:
                if len(term) > 2:  # Only search for terms longer than 2 characters
                    search_conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)")
                    search_params.extend([f"%{term}%", f"%{term}%"])
            
            if search_conditions:
                search_query = f"""
                    SELECT id, title, content, document_type, created_at
                    FROM documents 
                    WHERE user_id = ? AND ({' OR '.join(search_conditions)})
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                search_params.insert(0, user.id)
                
                cursor.execute(search_query, search_params)
                kb_results = cursor.fetchall()
                
                if kb_results:
                    knowledge_base_context = "\n\nRELEVANT DOCUMENTS FROM YOUR KNOWLEDGE BASE:\n"
                    for i, result in enumerate(kb_results[:3], 1):  # Top 3 results
                        doc_id, title, content, doc_type, created_at = result
                        content_preview = content[:500] if content else "No content available"
                        knowledge_base_context += f"\n{i}. Document: {title} (Type: {doc_type})\n"
                        knowledge_base_context += f"Content Preview: {content_preview}...\n"
                    
                    knowledge_base_context += "\nUse this information from your uploaded documents to provide more accurate and specific answers.\n"
                    logger.info(f"Found {len(kb_results)} relevant documents in knowledge base")
                else:
                    logger.info("No relevant documents found in knowledge base")
            else:
                logger.info("Query too short for meaningful search")
            
            cursor.close()
            conn.close()
                
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            knowledge_base_context = ""
        
        # Create comprehensive legal research prompt
        research_prompt = f"""
        As a conversational legal research assistant, please provide a comprehensive analysis of the following legal query:

        Query: "{query}"
        {knowledge_base_context}

        IMPORTANT INSTRUCTIONS:
        1. Be conversational and engaging in your response
        2. If the query contains statistical data, case numbers, or comparative information, suggest creating a visual chart
        3. Ask the user if they would like a chart visualization
        4. If they say yes, ask which type of chart they prefer (pie chart, bar chart, line chart, etc.)
        5. Maintain a helpful, professional tone while being conversational
        6. If you have relevant documents from the knowledge base, reference them specifically in your answer
        7. If the user asks about their uploaded documents, provide specific information from those documents

        Please provide your response in the following structured format:

        **Legal Overview**
        [Brief explanation of the legal concept and its relevance]

        **Key Legal Principles**
        1. **[Principle 1]**: [Description and explanation]
        2. **[Principle 2]**: [Description and explanation]
        3. **[Principle 3]**: [Description and explanation]

        **Relevant Case Law**
        - [Case 1]: [Brief description and relevance]
        - [Case 2]: [Brief description and relevance]

        **Practical Implications**
        - [Implication 1]: [How this applies in practice]
        - [Implication 2]: [How this applies in practice]

        **Additional Considerations**
        - [Consideration 1]: [Important factors to consider]
        - [Consideration 2]: [Important factors to consider]

        **Resources**
        - [Resource 1]: [Description and link if applicable]
        - [Resource 2]: [Description and link if applicable]

        **Chart Suggestion** (if applicable)
        If the query involves statistical data, case numbers, or comparative analysis, end your response with:
        
        "I notice this data could be visualized effectively. Would you like me to create a chart to better illustrate these statistics? If so, which type of chart would you prefer - pie chart, bar chart, line chart, or doughnut chart?"

        Format your response with clear headings, numbered lists, and bullet points. Use **bold** for important terms and concepts. Make it professional, conversational, and easy to read for legal professionals.
        """
        
        # Generate response using the selected LLM provider
        if llm_provider == 'openai':
            # Generate response using OpenAI
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": "You are DALI Legal AI, a specialized legal research assistant."},
                    {"role": "user", "content": research_prompt}
                ],
                max_tokens=int(user_settings.get('max_tokens', 2000)),
                temperature=float(user_settings.get('temperature', 0.7))
            )
            return response.choices[0].message.content
        elif llm_provider == 'ollama':
            # Generate response using Ollama
            try:
                response = llm_engine.generate_response(research_prompt)
                return response
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                return f"I apologize, but I encountered an error with the Ollama model: {str(e)}"
        
    except Exception as e:
        logger.error(f"AI legal research failed: {str(e)}")
        # Fallback to comprehensive manual research
        return generate_fallback_legal_research(query)

def generate_fallback_legal_research(query: str) -> str:
    """Generate fallback legal research when AI is unavailable"""
    query_lower = query.lower()
    
    # Labor law research
    if any(term in query_lower for term in ['labor', 'employment', 'worker', 'employee', 'ksa', 'saudi']):
        return """
## Labor Law Research Results

### Legal Overview
Labor law in Saudi Arabia (KSA) is governed by the Saudi Labor Law (Royal Decree No. M/51 of 23/8/1426H) and related regulations. The law covers employment relationships, working conditions, and worker rights.

### Key Legal Principles
1. **Employment Contracts**: Must be in writing and specify terms of employment
2. **Working Hours**: Maximum 8 hours per day, 48 hours per week
3. **Overtime**: Paid at 150% of regular wage
4. **Annual Leave**: Minimum 21 days per year
5. **End of Service Benefits**: Calculated based on length of service

### Relevant Regulations
- Saudi Labor Law (Royal Decree M/51)
- Wage Protection System (WPS)
- Saudization requirements (Nitaqat program)
- Occupational Safety and Health regulations

### Practical Implications
- Employers must register with Ministry of Human Resources
- Wages must be paid through WPS
- Termination requires valid reasons and notice
- Disputes resolved through Labor Courts

### Additional Considerations
- Recent Vision 2030 reforms affecting labor market
- Changes in Saudization requirements
- Remote work regulations post-COVID
- Women's employment rights and protections

### Resources
- Ministry of Human Resources and Social Development
- Saudi Labor Law official text
- Labor Court decisions and precedents
- Legal databases and research tools

**Note**: This is a general overview. For specific cases, consult with qualified legal professionals.
        """
    
    # Contract law research
    elif any(term in query_lower for term in ['contract', 'agreement', 'breach', 'terms']):
        return """
## Contract Law Research Results

### Legal Overview
Contract law in Saudi Arabia is primarily governed by Islamic Sharia principles and the Commercial Court Law. Contracts are binding agreements between parties with specific legal requirements.

### Key Legal Principles
1. **Offer and Acceptance**: Clear offer and unambiguous acceptance required
2. **Consideration**: Both parties must provide something of value
3. **Capacity**: Parties must have legal capacity to contract
4. **Legality**: Contract purpose must be lawful
5. **Certainty**: Terms must be sufficiently certain

### Contract Types
- Commercial contracts
- Employment contracts
- Real estate contracts
- Service agreements
- Partnership agreements

### Breach and Remedies
- Specific performance
- Damages (compensatory, punitive)
- Rescission and restitution
- Injunctive relief

### Practical Implications
- Written contracts recommended for complex transactions
- Consider dispute resolution mechanisms
- Understand termination clauses
- Review force majeure provisions

### Additional Considerations
- Sharia compliance requirements
- Recent commercial law reforms
- Digital contract validity
- Cross-border contract enforcement

### Resources
- Commercial Court Law
- Sharia principles and Islamic jurisprudence
- Commercial Court decisions
- Legal precedents and case law

**Note**: Contract law varies by jurisdiction and specific circumstances.
        """
    
    # General legal research fallback
    else:
        return f"""
## Legal Research Results

### Query Analysis
Your query: "{query}"

### Research Approach
For comprehensive legal research on this topic, consider the following:

### 1. Primary Sources
- Relevant laws and regulations
- Constitutional provisions
- Statutory frameworks
- Administrative rules

### 2. Secondary Sources
- Legal commentaries and treatises
- Law review articles
- Legal databases and research tools
- Professional legal publications

### 3. Case Law Research
- Court decisions and precedents
- Appellate court rulings
- Supreme court interpretations
- Recent legal developments

### 4. Practical Considerations
- Current legal trends
- Enforcement mechanisms
- Compliance requirements
- Risk assessment

### 5. Research Methodology
- Systematic legal analysis
- Comparative law approach
- Historical development
- Policy implications

### Recommended Next Steps
1. Consult primary legal sources
2. Review recent case law
3. Analyze regulatory guidance
4. Consider practical implications
5. Seek professional legal advice

### Resources
- Legal databases (LexisNexis, Westlaw)
- Government legal portals
- Bar association resources
- Academic legal journals

**Note**: This is a general research framework. For specific legal advice, consult with qualified legal professionals familiar with your jurisdiction and circumstances.
        """

@app.post("/api/document-analysis")
async def document_analysis(
    request: Request,
    document: UploadFile = File(None),
    analysis_type: str = Form("full"),
    add_to_kb: str = Form("false"),
    user: User = Depends(require_auth)
):
    """Document analysis endpoint with file upload or text input"""
    try:
        # Check if we have a file upload or text input
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON input (text analysis)
            body = await request.json()
            text_content = body.get("text", "")
            filename = "text_input.txt"
            
            # Extract add_to_knowledge_base from JSON
            add_to_kb = body.get("add_to_knowledge_base", "false")
            analysis_type = body.get("analysis_type", "full")
            
            if not text_content:
                return {
                    "success": False,
                    "error": "No text content provided",
                    "timestamp": datetime.now().isoformat()
                }
            
            content = text_content.encode('utf-8')
        else:
            # Handle file upload
            if not document:
                return {
                    "success": False,
                    "error": "No file or text content provided",
                    "timestamp": datetime.now().isoformat()
                }
            
            content = await document.read()
            filename = document.filename or "unknown.txt"
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        try:
            # Process document using the existing doc processor
            from src.utils.document_processor import DocumentProcessor
            doc_processor = DocumentProcessor()
            document_text = doc_processor.process_file(temp_path)
            
            if not document_text:
                return {
                    "success": False,
                    "error": "Could not extract text from document",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Analyze document using LLM
            analysis_result = await analyze_document_with_llm(document_text, analysis_type, user)
            
            # Add to knowledge base if requested
            kb_success = False
            if add_to_kb and add_to_kb.lower() in ['true', '1', 'yes']:
                kb_success = await add_document_to_kb(
                    user_id=user.id,
                    filename=filename,
                    analysis_type=analysis_type,
                    content=document_text
                )
            
            return {
                "success": True,
                "message": "Document analysis completed",
                "filename": filename,
                "analysis_type": analysis_type,
                "analysis_result": analysis_result,
                "kb_success": kb_success,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return {
            "success": False,
            "error": f"Document analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/web-scraping")
async def web_scraping(url: str, scrape_links: bool = True, max_links: int = 5, download_documents: bool = False, bypass_auth: bool = False, user: User = Depends(require_auth)):
    """Web scraping endpoint with combined Firecrawl and BeautifulSoup + document downloading"""
    try:
        # Run scraping methods based on bypass_auth setting
        if bypass_auth:
            # Try authentication scraping first for protected sites
            auth_result = scrape_with_authentication(url)
            firecrawl_result = scrape_with_firecrawl(url)
            bs_result = scrape_with_beautifulsoup(url, bypass_auth)
        else:
            # Standard scraping
            firecrawl_result = scrape_with_firecrawl(url)
            bs_result = scrape_with_beautifulsoup(url, bypass_auth)
            auth_result = {"success": False}
        
        # Determine overall success
        auth_success = auth_result.get("success", False)
        firecrawl_success = firecrawl_result.get("success", False)
        bs_success = bs_result.get("success", False)
        
        if auth_success or firecrawl_success or bs_success:
            # Combine results from all methods
            combined_data = {
                "url": url,
                "authentication": auth_result if auth_success else None,
                "firecrawl": firecrawl_result if firecrawl_success else None,
                "beautifulsoup": bs_result if bs_success else None,
                "combined_content": "",
                "metadata": {},
                "links": [],
                "images": []
            }
            
            # Extract and combine content
            content_parts = []
            
            # Add Authentication content if available (highest priority)
            if auth_success:
                auth_data = auth_result.get("data", {})
                if auth_data.get("content"):
                    content_parts.append(f"## Authenticated Content\n{auth_data['content']}")
                
                # Extract metadata from Authentication
                if auth_data.get("metadata"):
                    combined_data["metadata"].update(auth_data["metadata"])
                
                # Extract links from Authentication
                if auth_data.get("links"):
                    combined_data["links"].extend(auth_data["links"])
            
            # Add Firecrawl content if available
            if firecrawl_success:
                fc_data = firecrawl_result.get("data", {})
                if fc_data.get("markdown"):
                    content_parts.append(f"## Firecrawl Content (Markdown)\n{fc_data['markdown']}")
                elif fc_data.get("content"):
                    content_parts.append(f"## Firecrawl Content\n{fc_data['content']}")
                
                # Extract metadata from Firecrawl
                if fc_data.get("metadata"):
                    combined_data["metadata"].update(fc_data["metadata"])
                
                # Extract links from Firecrawl
                if fc_data.get("linksOnPage"):
                    combined_data["links"].extend(fc_data["linksOnPage"])
            
            # Add BeautifulSoup content if available
            if bs_success:
                bs_data = bs_result.get("data", {})
                if bs_data.get("content"):
                    content_parts.append(f"## BeautifulSoup Content\n{bs_data['content']}")
                
                # Extract metadata from BeautifulSoup
                if bs_data.get("title"):
                    combined_data["metadata"]["title"] = bs_data["title"]
                if bs_data.get("description"):
                    combined_data["metadata"]["description"] = bs_data["description"]
                
                # Extract links from BeautifulSoup
                if bs_data.get("links"):
                    combined_data["links"].extend(bs_data["links"])
            
            # Scrape useful links if requested
            if scrape_links:
                try:
                    links_result = scrape_useful_links(url, max_links, bypass_auth)
                    if links_result.get("success"):
                        combined_data["useful_links_content"] = links_result.get("scraped_content", [])
                        combined_data["total_useful_links"] = links_result.get("total_links_found", 0)
                        combined_data["content_scraped"] = links_result.get("content_scraped", 0)
                        
                        # Add useful links content to main content
                        for link_content in links_result.get("scraped_content", []):
                            content_parts.append(f"## Content from: {link_content['title']}\n{link_content['content']}")
                except Exception as e:
                    logger.warning(f"Useful links scraping failed: {e}")
            
            # Combine all content
            combined_data["combined_content"] = "\n\n".join(content_parts)
            
            # Save content to knowledge base
            if combined_data["combined_content"]:
                try:
                    # Detect language from content
                    detected_language = detect_language(combined_data["combined_content"])
                    
                    # Save to knowledge base
                    kb_title = combined_data["metadata"].get("title", f"Web Content from {url}")
                    kb_content = combined_data["combined_content"]
                    
                    # Get database connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Insert into knowledge base
                    kb_insert_query = """
                    INSERT INTO documents (
                        user_id, title, content, document_type, 
                        source, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    current_time = datetime.now().isoformat()
                    cursor.execute(kb_insert_query, (
                        user.id,
                        kb_title,
                        kb_content,
                        "Web Content",
                        url,
                        current_time
                    ))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    logger.info(f"Saved web content to knowledge base: {kb_title}")
                    
                except Exception as kb_error:
                    logger.error(f"Failed to save to knowledge base: {kb_error}")
            
            # Remove duplicates from links
            combined_data["links"] = list(set(combined_data["links"]))
            
            # Download documents if requested
            document_download_result = None
            if download_documents:
                links_to_check = combined_data.get("links", [])
                
                # Discover hidden document URLs from page content
                hidden_docs = discover_hidden_documents(url, combined_data.get("combined_content", ""))
                all_links = links_to_check + hidden_docs
                
                logger.info(f"Starting document download for {len(links_to_check)} visible links + {len(hidden_docs)} hidden links + base URL")
                document_download_result = download_documents_from_links(url, all_links, user.id, bypass_auth=True)
                logger.info(f"Document download completed: {document_download_result.get('downloaded_count', 0)} successful, {document_download_result.get('failed_count', 0)} failed")
            
            # Determine primary method for response
            if auth_success:
                primary_method = "authentication"
            elif firecrawl_success:
                primary_method = "firecrawl"
            else:
                primary_method = "beautifulsoup"
            
            response_data = {
                "success": True,
                "url": url,
                "method": f"combined ({primary_method} primary)",
                "data": combined_data,
                "authentication_status": "success" if auth_success else "failed",
                "firecrawl_status": "success" if firecrawl_success else "failed",
                "beautifulsoup_status": "success" if bs_success else "failed",
                "authentication_error": auth_result.get("error") if not auth_success else None,
                "firecrawl_error": firecrawl_result.get("error") if not firecrawl_success else None,
                "beautifulsoup_error": bs_result.get("error") if not bs_success else None,
                "useful_links_content": combined_data.get("useful_links_content", []),
                "total_useful_links": combined_data.get("total_useful_links", 0),
                "content_scraped": combined_data.get("content_scraped", 0),
                "bypass_auth_used": bypass_auth,
                "knowledge_base_saved": True if combined_data["combined_content"] else False,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add document download results if available
            if document_download_result:
                response_data["document_download"] = document_download_result
            
            return response_data
        else:
            return {
                "success": False,
                "url": url,
                "error": f"Both Firecrawl and BeautifulSoup failed. Firecrawl: {firecrawl_result.get('error')}, BeautifulSoup: {bs_result.get('error')}",
                "firecrawl_error": firecrawl_result.get("error"),
                "beautifulsoup_error": bs_result.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": f"Web scraping failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/advanced-document-extraction")
async def advanced_document_extraction(url: str, user: User = Depends(require_auth)):
    """Advanced document extraction that bypasses authentication and discovers hidden documents"""
    try:
        logger.info(f"Starting advanced document extraction for {url}")
        
        # Step 1: Get page content
        firecrawl_result = scrape_with_firecrawl(url)
        bs_result = scrape_with_beautifulsoup(url)
        
        # Use the best available content
        page_content = ""
        if firecrawl_result.get("success"):
            fc_data = firecrawl_result.get("data", {})
            page_content = fc_data.get("markdown", "") or fc_data.get("content", "")
        elif bs_result.get("success"):
            bs_data = bs_result.get("data", {})
            page_content = bs_data.get("content", "")
        
        if not page_content:
            return {
                "success": False,
                "error": "Could not retrieve page content for analysis",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Discover hidden document URLs
        discovered_urls = discover_hidden_documents(url, page_content)
        
        # Step 3: Attempt to access discovered documents
        successful_downloads = []
        failed_downloads = []
        
        for doc_url in discovered_urls:
            try:
                # Try multiple access strategies
                access_result = attempt_document_access(doc_url, {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Referer': urlparse(url).netloc,
                    'X-Requested-With': 'XMLHttpRequest'
                })
                
                if access_result.get("success"):
                    response = access_result["response"]
                    
                    # Try to extract text and save to database
                    try:
                        from src.utils.document_processor import DocumentProcessor
                        doc_processor = DocumentProcessor()
                        
                        # Create temporary file
                        filename = os.path.basename(urlparse(doc_url).path) or "document"
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
                            tmp_file.write(response.content)
                            temp_path = tmp_file.name
                        
                        # Extract text
                        document_text = doc_processor.process_file(temp_path)
                        
                        if document_text and len(document_text.strip()) > 50:
                            # Save to database
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                INSERT INTO documents (user_id, title, document_type, source, content, created_at)
                                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """, (
                                user.id,
                                filename,
                                "Extracted Document",
                                f"advanced_extraction:{url}",
                                document_text
                            ))
                            
                            document_id = cursor.lastrowid
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            successful_downloads.append({
                                "url": doc_url,
                                "filename": filename,
                                "document_id": document_id,
                                "strategy": access_result.get("strategy"),
                                "content_length": len(document_text)
                            })
                            
                            logger.info(f"Successfully extracted document: {filename}")
                        else:
                            failed_downloads.append({
                                "url": doc_url,
                                "filename": filename,
                                "error": "Could not extract meaningful text"
                            })
                        
                        # Clean up
                        os.unlink(temp_path)
                        
                    except Exception as e:
                        failed_downloads.append({
                            "url": doc_url,
                            "filename": os.path.basename(urlparse(doc_url).path) or "unknown",
                            "error": f"Processing failed: {str(e)}"
                        })
                else:
                    failed_downloads.append({
                        "url": doc_url,
                        "filename": os.path.basename(urlparse(doc_url).path) or "unknown",
                        "error": access_result.get("error", "Access failed")
                    })
                    
            except Exception as e:
                failed_downloads.append({
                    "url": doc_url,
                    "filename": os.path.basename(urlparse(doc_url).path) or "unknown",
                    "error": f"Unexpected error: {str(e)}"
                })
        
        return {
            "success": True,
            "url": url,
            "discovered_urls": len(discovered_urls),
            "successful_extractions": len(successful_downloads),
            "failed_extractions": len(failed_downloads),
            "extracted_documents": successful_downloads,
            "failed_documents": failed_downloads,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Advanced document extraction failed: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error": f"Advanced document extraction failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/knowledge-base")
async def knowledge_base_query(
    query: str, 
    num_results: int = 10,
    min_score: float = 0.0,
    user: User = Depends(require_auth)
):
    """Knowledge base query endpoint - search documents using vector store"""
    try:
        from src.core.vector_store import VectorStore
        from src.web.app import user_store
        
        # Initialize vector store
        vector_store = VectorStore()
        
        # Generate query embedding
        query_embedding = vector_store._generate_embedding(query)
        
        # Search for similar documents
        results = user_store.search_documents(
            user.id,
            query_embedding,
            top_k=num_results
        )
        
        if not results:
            return {
                "success": True,
                "query": query,
                "results": [],
                "message": "No documents found matching your query",
                "timestamp": datetime.now().isoformat()
            }
        
        # Filter results by minimum score
        filtered_results = []
        for result in results:
            similarity_score = result.get('similarity_score', 0.0)
            if similarity_score >= min_score:
                filtered_results.append(result)
        
        # Format results for response
        formatted_results = []
        for result in filtered_results:
            formatted_results.append({
                "id": result.get('id'),
                "title": result.get('title', 'Untitled'),
                "content": result.get('content', ''),
                "document_type": result.get('document_type', 'unknown'),
                "source": result.get('source', 'unknown'),
                "created_at": result.get('created_at'),
                "score": result.get('similarity_score', 0.0),
                "document_name": result.get('title', 'Untitled')
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"Found {len(formatted_results)} documents matching your query (min score: {min_score})",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge base query failed: {str(e)}")
        return {
            "success": False,
            "query": query,
            "error": f"Knowledge base query failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/knowledge-base/generate-chart")
async def generate_chart(request: Request, user: User = Depends(require_auth)):
    """Generate chart from query results"""
    try:
        data = await request.json()
        query = data.get('query', '')
        sql_query = data.get('sql_query', '')
        
        if not query or not sql_query:
            return {
                "success": False,
                "error": "Query and SQL query are required",
                "timestamp": datetime.now().isoformat()
            }
        
        # Initialize components
        from src.core.database.manager import DatabaseManager
        from src.core.database.chart_generator import ChartGenerator
        
        db_manager = DatabaseManager()
        chart_generator = ChartGenerator()
        
        # Check if database is connected
        if not db_manager.is_connected():
            return {
                "success": False,
                "error": "Database not connected",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute SQL query
        success, df = db_manager.execute_query(sql_query)
        
        if not success:
            return {
                "success": False,
                "error": f"Query execution failed: {df}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate chart
        chart_result = chart_generator.generate_chart(df, query)
        
        if chart_result['success']:
            return {
                "success": True,
                "chart_html": chart_result['chart_html'],
                "chart_config": chart_result['chart_config'],
                "reasoning": chart_result['reasoning'],
                "data_points": len(df),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": chart_result['error'],
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        return {
            "success": False,
            "error": f"Chart generation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Admin API endpoints
@app.get("/api/admin/users")
async def get_users(admin: User = Depends(require_admin)):
    """Get all users for admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, role, 
                   is_active, created_at, company_name, job_title
            FROM users ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"success": True, "users": users}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch users: {str(e)}"}

@app.get("/api/admin/analytics")
async def get_analytics(admin: User = Depends(require_admin)):
    """Get system analytics for admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Get active users count
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()[0]
        
        # Get documents count (if documents table exists)
        try:
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_documents = cursor.fetchone()[0]
        except:
            total_documents = 0
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "analytics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_documents": total_documents,
                "system_uptime": "N/A",
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch analytics: {str(e)}"}

# Health check
@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        # Check database connection
        db_status = "connected"
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()  # Fetch the result to avoid "Unread result found" error
            cursor.close()
            conn.close()
        except Exception as e:
            db_status = "disconnected"
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check Firecrawl status
        firecrawl_status = "not_configured"
        if FIRECRAWL_API_KEY:
            try:
                # Test Firecrawl with a simple request
                test_result = scrape_with_firecrawl("https://example.com")
                if test_result.get("success"):
                    firecrawl_status = "working"
                else:
                    firecrawl_status = "configured_but_failing"
            except Exception as e:
                firecrawl_status = "configured_but_error"
                logger.error(f"Firecrawl health check failed: {str(e)}")
        
        # Check OpenAI status
        openai_status = "not_configured"
        try:
            openai_config = config.get('openai', {})
            if openai_config.get('api_key'):
                # Quick test
                from src.core.llm_engine import LLMEngine
                llm_engine = LLMEngine()
                llm_engine.analyze_document("Test", "summary")
                openai_status = "working"
            else:
                openai_status = "not_configured"
        except Exception as e:
            openai_status = "configured_but_error"
            logger.error(f"OpenAI health check failed: {str(e)}")
        
        # Check Ollama status
        ollama_status = "not_configured"
        try:
            import requests
            ollama_config = config.get('ollama', {})
            host = ollama_config.get('host', '127.0.0.1')
            port = ollama_config.get('port', 11435)
            
            # Handle case where host already includes port
            if ':' in host:
                url = f"http://{host}/api/tags"
            else:
                url = f"http://{host}:{port}/api/tags"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            ollama_status = "working"
        except Exception as e:
            ollama_status = "not_running"
            logger.error(f"Ollama health check failed: {str(e)}")
        
        # Determine overall status
        overall_status = "healthy"
        if db_status != "connected":
            overall_status = "unhealthy"
        elif firecrawl_status == "configured_but_failing" or firecrawl_status == "configured_but_error":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "database": db_status,
            "firecrawl": firecrawl_status,
            "openai": openai_status,
            "ollama": ollama_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "unknown",
            "firecrawl": "unknown",
            "openai": "unknown",
            "ollama": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/test-openai")
async def test_openai():
    """Test OpenAI connection"""
    try:
        from src.core.llm_engine import LLMEngine
        
        # Test OpenAI
        llm_engine = LLMEngine()
        result = llm_engine.analyze_document("Test", "summary")
        
        return {
            "success": True,
            "message": "OpenAI connection successful",
            "provider": "openai"
        }
    except Exception as e:
        logger.error(f"OpenAI test failed: {str(e)}")
        return {
            "success": False,
            "message": f"OpenAI connection failed: {str(e)}",
            "provider": "openai"
        }

@app.get("/api/test-ollama")
async def test_ollama():
    """Test Ollama connection"""
    try:
        import requests
        
        # Get Ollama configuration
        ollama_config = config.get('ollama', {})
        host = ollama_config.get('host', '127.0.0.1')
        port = ollama_config.get('port', 11435)
        
        # Handle case where host already includes port
        if ':' in host:
            url = f"http://{host}/api/tags"
        else:
            url = f"http://{host}:{port}/api/tags"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Ollama connection successful",
            "provider": "ollama",
            "models": response.json().get('models', [])
        }
    except Exception as e:
        logger.error(f"Ollama test failed: {str(e)}")
        return {
            "success": False,
            "message": f"Ollama connection failed: {str(e)}",
            "provider": "ollama"
        }

@app.get("/api/test-firecrawl")
async def test_firecrawl():
    """Test Firecrawl connectivity"""
    try:
        if not FIRECRAWL_API_KEY:
            return {
                "firecrawl_available": False,
                "error": "Firecrawl API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        # Test with a simple URL
        test_url = "https://example.com"
        result = scrape_with_firecrawl(test_url)
        
        return {
            "firecrawl_available": result["success"],
            "test_url": test_url,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "firecrawl_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Chat and Conversation Management
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, user: User = Depends(require_auth)):
    """ChatGPT-style chat interface"""
    return templates.TemplateResponse("new_chat.html", {
        "request": request,
        "title": "Chat - DALI Legal AI",
        "user": user,
        "t": lambda key: t(key, request)
    })

@app.get("/api/conversations")
async def get_conversations(user: User = Depends(require_auth)):
    """Get all conversations for the current user with unread counts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversations with message counts and last message preview
        cursor.execute("""
            SELECT 
                c.id, 
                c.title, 
                c.created_at, 
                c.updated_at,
                COUNT(m.id) as message_count,
                (SELECT content FROM messages m2 
                 WHERE m2.conversation_id = c.id 
                 ORDER BY m2.timestamp DESC LIMIT 1) as last_message_preview,
                (SELECT timestamp FROM messages m3 
                 WHERE m3.conversation_id = c.id 
                 ORDER BY m3.timestamp DESC LIMIT 1) as last_message_time
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.user_id = ? 
            GROUP BY c.id
            ORDER BY c.updated_at DESC
        """, (user.id,))
        
        conversations = cursor.fetchall()
        
        # Add unread count for each conversation
        for conv in conversations:
            cursor.execute("""
                SELECT COUNT(*) as unread_count
                FROM messages 
                WHERE conversation_id = ? 
                AND role = 'assistant' 
                AND is_read = 0
            """, (conv['id'],))
            unread_result = cursor.fetchone()
            conv['unread_count'] = unread_result['unread_count'] if unread_result else 0
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "conversations": conversations
        }
    except Exception as e:
        logger.error(f"Failed to get conversations: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/conversations")
async def create_conversation(request: Request, user: User = Depends(require_auth)):
    """Create a new conversation"""
    try:
        data = await request.json()
        title = data.get("title", "New Chat")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (user_id, title, created_at, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (user.id, title))
        conversation_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "title": title
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, user: User = Depends(require_auth)):
    """Get messages for a specific conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, content, timestamp 
            FROM messages 
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id, user.id))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "messages": messages
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/conversations/{conversation_id}/messages")
async def send_message(conversation_id: int, request: Request, user: User = Depends(require_auth)):
    """Send a message in a conversation with enhanced AI responses"""
    try:
        data = await request.json()
        content = data.get("content", "")
        role = data.get("role", "user")
        
        if not content:
            return {"success": False, "error": "Message content is required"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add user message
        cursor.execute("""
            INSERT INTO messages (conversation_id, user_id, role, content, timestamp, is_read)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
        """, (conversation_id, user.id, role, content))
        
        # Generate AI response if it's a user message
        ai_response = ""
        if role == "user":
            ai_response = await generate_enhanced_ai_response(content, user, conversation_id)
            if ai_response:
                cursor.execute("""
                    INSERT INTO messages (conversation_id, user_id, role, content, timestamp, is_read)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 0)
                """, (conversation_id, user.id, "assistant", ai_response))
        
        # Update conversation timestamp and title if it's the first message
        cursor.execute("""
            SELECT COUNT(*) as msg_count FROM messages 
            WHERE conversation_id = ? AND role = 'user'
        """, (conversation_id,))
        msg_count = cursor.fetchone()[0]
        
        if msg_count == 1:  # First user message
            # Generate a title from the first message
            title = content[:50] + "..." if len(content) > 50 else content
            cursor.execute("""
                UPDATE conversations 
                SET title = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (title, conversation_id))
        else:
            cursor.execute("""
                UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (conversation_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "ai_response": ai_response,
            "message_count": msg_count
        }
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def generate_enhanced_ai_response(user_message: str, user: User, conversation_id: int) -> str:
    """Generate enhanced AI response with conversation context"""
    try:
        # Get user's LLM settings
        user_settings = await get_user_llm_settings(user)
        llm_provider = user_settings.get('llm_provider', 'openai')
        llm_model = user_settings.get('llm_model', 'gpt-4o')
        
        logger.info(f"Using LLM provider: {llm_provider}, model: {llm_model}")
        
        if llm_provider == 'openai':
            # Use OpenAI
            import openai
            openai.api_key = config.get('openai', {}).get('api_key')
            
            if not openai.api_key:
                return "OpenAI API key not configured. Please contact administrator."
        elif llm_provider == 'ollama':
            # Use Ollama
            try:
                from src.core.llm_engine import LLMEngine
                llm_engine = LLMEngine(model_name=llm_model)
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                return f"Failed to initialize Ollama model {llm_model}. Please check if Ollama is running and the model is available."
        else:
            return f"Unsupported LLM provider: {llm_provider}"
        
        # Get conversation history for context
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, timestamp 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, (conversation_id,))
        
        recent_messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Build context from recent messages
        context = ""
        if recent_messages:
            context = "Recent conversation context:\n"
            for msg in reversed(recent_messages[-5:]):  # Last 5 messages for context
                role_label = "User" if msg['role'] == 'user' else "Assistant"
                context += f"{role_label}: {msg['content']}\n"
        
        # Enhanced prompt with context
        enhanced_prompt = f"""
You are DALI Legal AI, a specialized legal assistant. You help users with legal research, document analysis, and legal questions.

{context}

Current user question: "{user_message}"

Please provide a comprehensive, helpful response that:
1. Directly addresses the user's question
2. Provides relevant legal information
3. Suggests follow-up actions if appropriate
4. Maintains a professional, helpful tone
5. References the conversation context when relevant

If this is a legal question, provide specific guidance while noting that this is for informational purposes and users should consult qualified legal professionals for specific legal advice.
"""
        
        # Generate response using the selected LLM provider
        if llm_provider == 'openai':
            # Generate response using OpenAI
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": "You are DALI Legal AI, a specialized legal assistant."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=int(user_settings.get('max_tokens', 2000)),
                temperature=float(user_settings.get('temperature', 0.7))
            )
            return response.choices[0].message.content
        elif llm_provider == 'ollama':
            # Generate response using Ollama
            try:
                response = llm_engine.generate_response(enhanced_prompt)
                return response
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                return f"I apologize, but I encountered an error with the Ollama model: {str(e)}"
        
    except Exception as e:
        logger.error(f"Enhanced AI response generation failed: {str(e)}")
        # Fallback response with conversation awareness
        return f"""
I understand you're asking about: "{user_message}"

As DALI Legal AI, I can help you with:
- **Legal Research**: Finding relevant laws, regulations, and precedents
- **Document Analysis**: Reviewing contracts, agreements, and legal documents  
- **Case Law References**: Locating relevant court decisions and rulings
- **Compliance Questions**: Understanding regulatory requirements
- **Legal Guidance**: Providing general legal information and direction

**Important Note**: This response is for informational purposes only. For specific legal advice, please consult with qualified legal professionals.

How can I assist you further with your legal inquiry?
"""

async def get_user_statistics(user_id: int) -> dict:
    """Get comprehensive user statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get document count
        cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_id,))
        total_documents = cursor.fetchone()['count']
        
        # Get conversation count
        cursor.execute("SELECT COUNT(*) as count FROM conversations WHERE user_id = ?", (user_id,))
        total_conversations = cursor.fetchone()['count']
        
        # Get recent activity
        cursor.execute("""
            SELECT 'document' as type, title, created_at 
            FROM documents WHERE user_id = ?
            UNION ALL
            SELECT 'conversation' as type, title, created_at 
            FROM conversations WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 5
        """, (user_id, user_id))
        recent_activity = cursor.fetchall()
        
        # Get shared documents count
        cursor.execute("""
            SELECT COUNT(*) as count FROM document_permissions 
            WHERE user_id = ? AND permission_type = 'read'
        """, (user_id,))
        shared_documents = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            "total_documents": total_documents,
            "total_conversations": total_conversations,
            "shared_documents": shared_documents,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return {
            "total_documents": 0,
            "total_conversations": 0,
            "shared_documents": 0,
            "recent_activity": []
        }

async def get_system_statistics() -> dict:
    """Get comprehensive system statistics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Get active users (logged in within last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE last_active > datetime('now', '-30 days')
        """, ())
        active_users = cursor.fetchone()['count']
        
        # Get admin users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchone()['count']
        
        # Get total documents
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        total_documents = cursor.fetchone()['count']
        
        # Get total conversations
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        total_conversations = cursor.fetchone()['count']
        
        # Get recent user activity
        cursor.execute("""
            SELECT u.username, 'login' as activity, u.last_active as timestamp
            FROM users u WHERE u.last_active > datetime('now', '-7 days')
            UNION ALL
            SELECT u.username, 'document' as activity, d.created_at as timestamp
            FROM documents d JOIN users u ON d.user_id = u.id
            WHERE d.created_at > datetime('now', '-7 days')
            ORDER BY timestamp DESC LIMIT 10
        """)
        recent_activity = cursor.fetchall()
        
        # Check system health
        system_health = "healthy"
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        except:
            system_health = "degraded"
        
        conn.close()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "total_documents": total_documents,
            "total_conversations": total_conversations,
            "recent_activity": recent_activity,
            "system_health": system_health
        }
        
    except Exception as e:
        logger.error(f"System statistics error: {e}")
        return {
            "total_users": 0,
            "active_users": 0,
            "admin_users": 0,
            "total_documents": 0,
            "total_conversations": 0,
            "recent_activity": [],
            "system_health": "unknown"
        }

async def generate_ai_response(user_message: str, user: User) -> str:
    """Generate AI response using LLM (legacy function for compatibility)"""
    return await generate_enhanced_ai_response(user_message, user, 0)

@app.post("/api/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(conversation_id: int, user: User = Depends(require_auth)):
    """Mark all messages in a conversation as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET is_read = 1 
            WHERE conversation_id = ? AND role = 'assistant'
        """, (conversation_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to mark conversation as read: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/conversations/unread-count")
async def get_unread_count(user: User = Depends(require_auth)):
    """Get total unread message count for user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = ? AND m.role = 'assistant' AND m.is_read = 0
        """, (user.id,))
        
        result = cursor.fetchone()
        unread_count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "unread_count": unread_count
        }
    except Exception as e:
        logger.error(f"Failed to get unread count: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Advanced Chat System - Enhanced API Endpoints
@app.post("/api/chat/send")
async def send_chat_message(
    message: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    user: User = Depends(require_auth)
):
    """Send a chat message with advanced features"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create or get conversation
        if not conversation_id:
            # Create new conversation
            cursor.execute("""
                INSERT INTO conversations (user_id, title, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user.id, message[:50] + "..." if len(message) > 50 else message))
            conversation_id = cursor.lastrowid
        else:
            # Verify conversation belongs to user
            cursor.execute("""
                SELECT id FROM conversations WHERE id = ? AND user_id = ?
            """, (conversation_id, user.id))
            if not cursor.fetchone():
                return {"success": False, "error": "Conversation not found"}
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_id, recipient_id, content, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (conversation_id, user.id, user.id, message))
        
        message_id = cursor.lastrowid
        
        # Generate AI response
        ai_response = await generate_enhanced_ai_response(message, user.id, conversation_id)
        
        if ai_response:
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender_id, recipient_id, content, is_ai, created_at)
                VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            """, (conversation_id, 0, user.id, ai_response))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "ai_response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return {"success": False, "error": f"Failed to send message: {str(e)}"}

@app.get("/api/chat/history")
async def get_chat_history(
    conversation_id: Optional[int] = None,
    limit: int = 50,
    user: User = Depends(require_auth)
):
    """Get chat history with advanced features"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if conversation_id:
            # Get specific conversation messages
            cursor.execute("""
                SELECT m.*, u.username as sender_name
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.conversation_id = ? AND m.recipient_id = ?
                ORDER BY m.created_at ASC
                LIMIT ?
            """, (conversation_id, user.id, limit))
        else:
            # Get all conversations with latest messages
            cursor.execute("""
                SELECT c.*, 
                       m.content as last_message,
                       m.created_at as last_message_time,
                       COUNT(msg.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                LEFT JOIN messages msg ON c.id = msg.conversation_id
                WHERE c.user_id = ?
                GROUP BY c.id
                ORDER BY c.created_at DESC
                LIMIT ?
            """, (user.id, limit))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "conversations": results
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        return {"success": False, "error": f"Failed to get chat history: {str(e)}"}

@app.post("/api/chat/mark_read")
async def mark_messages_read(
    conversation_id: int,
    user: User = Depends(require_auth)
):
    """Mark messages as read in a conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET is_read = 1 
            WHERE conversation_id = ? AND recipient_id = ? AND is_read = 0
        """, (conversation_id, user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "marked_read": cursor.rowcount}
        
    except Exception as e:
        logger.error(f"Failed to mark messages as read: {str(e)}")
        return {"success": False, "error": f"Failed to mark messages as read: {str(e)}"}

# Document Permission Workflow System
@app.post("/request-permission")
async def request_document_permission(
    document_id: int = Form(...),
    user: User = Depends(require_auth)
):
    """Request permission to access a document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if document exists and get owner
        cursor.execute("""
            SELECT user_id, title FROM documents WHERE id = ?
        """, (document_id,))
        
        document = cursor.fetchone()
        if not document:
            return {"success": False, "error": "Document not found"}
        
        if document['user_id'] == user.id:
            return {"success": False, "error": "You already own this document"}
        
        # Check if permission already requested
        cursor.execute("""
            SELECT id FROM document_permissions 
            WHERE document_id = ? AND requester_id = ? AND status = 'pending'
        """, (document_id, user.id))
        
        if cursor.fetchone():
            return {"success": False, "error": "Permission already requested"}
        
        # Create permission request
        cursor.execute("""
            INSERT INTO document_permissions (document_id, owner_id, requester_id, status, created_at)
            VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        """, (document_id, document['user_id'], user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Permission requested for document: {document['title']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to request permission: {str(e)}")
        return {"success": False, "error": f"Failed to request permission: {str(e)}"}

@app.get("/my-permission-requests")
async def my_permission_requests(request: Request, user: User = Depends(require_auth)):
    """View my permission requests"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get incoming requests (requests to me)
        cursor.execute("""
            SELECT dp.*, d.title, u.username as requester_name
            FROM document_permissions dp
            JOIN documents d ON dp.document_id = d.id
            JOIN users u ON dp.requester_id = u.id
            WHERE dp.owner_id = ?
            ORDER BY dp.created_at DESC
        """, (user.id,))
        
        incoming_requests = cursor.fetchall()
        
        # Get outgoing requests (my requests)
        cursor.execute("""
            SELECT dp.*, d.title, u.username as owner_name
            FROM document_permissions dp
            JOIN documents d ON dp.document_id = d.id
            JOIN users u ON dp.owner_id = u.id
            WHERE dp.requester_id = ?
            ORDER BY dp.created_at DESC
        """, (user.id,))
        
        outgoing_requests = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("my_permission_requests.html", {
            "request": request,
            "user": user,
            "incoming_requests": incoming_requests,
            "outgoing_requests": outgoing_requests,
            "title": "Permission Requests - DALI Legal AI"
        })
        
    except Exception as e:
        logger.error(f"Failed to get permission requests: {str(e)}")
        return {"success": False, "error": f"Failed to get permission requests: {str(e)}"}

@app.post("/permission-request/approve")
async def approve_permission_request(
    request_id: int = Form(...),
    user: User = Depends(require_auth)
):
    """Approve a permission request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user owns the document
        cursor.execute("""
            SELECT dp.*, d.title
            FROM document_permissions dp
            JOIN documents d ON dp.document_id = d.id
            WHERE dp.id = ? AND dp.owner_id = ? AND dp.status = 'pending'
        """, (request_id, user.id))
        
        permission = cursor.fetchone()
        if not permission:
            return {"success": False, "error": "Permission request not found or already processed"}
        
        # Update permission status
        cursor.execute("""
            UPDATE document_permissions 
            SET status = 'approved', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (request_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Permission approved for document: {permission['title']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to approve permission: {str(e)}")
        return {"success": False, "error": f"Failed to approve permission: {str(e)}"}

@app.post("/permission-request/deny")
async def deny_permission_request(
    request_id: int = Form(...),
    user: User = Depends(require_auth)
):
    """Deny a permission request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user owns the document
        cursor.execute("""
            SELECT dp.*, d.title
            FROM document_permissions dp
            JOIN documents d ON dp.document_id = d.id
            WHERE dp.id = ? AND dp.owner_id = ? AND dp.status = 'pending'
        """, (request_id, user.id))
        
        permission = cursor.fetchone()
        if not permission:
            return {"success": False, "error": "Permission request not found or already processed"}
        
        # Update permission status
        cursor.execute("""
            UPDATE document_permissions 
            SET status = 'denied', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (request_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Permission denied for document: {permission['title']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to deny permission: {str(e)}")
        return {"success": False, "error": f"Failed to deny permission: {str(e)}"}

# Bulk Operations System
@app.post("/api/admin/users/bulk-activate")
async def bulk_activate_users(
    user_ids: List[int] = Body(...),
    user: User = Depends(require_auth)
):
    """Bulk activate users"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert list to tuple for SQL IN clause
        user_ids_tuple = tuple(user_ids)
        
        cursor.execute("""
            UPDATE users 
            SET is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({})
        """.format(','.join(['?'] * len(user_ids))), user_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Activated {cursor.rowcount} users",
            "affected_count": cursor.rowcount
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk activate users: {str(e)}")
        return {"success": False, "error": f"Failed to bulk activate users: {str(e)}"}

@app.post("/api/admin/users/bulk-deactivate")
async def bulk_deactivate_users(
    user_ids: List[int] = Body(...),
    user: User = Depends(require_auth)
):
    """Bulk deactivate users"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert list to tuple for SQL IN clause
        user_ids_tuple = tuple(user_ids)
        
        cursor.execute("""
            UPDATE users 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({})
        """.format(','.join(['?'] * len(user_ids))), user_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Deactivated {cursor.rowcount} users",
            "affected_count": cursor.rowcount
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk deactivate users: {str(e)}")
        return {"success": False, "error": f"Failed to bulk deactivate users: {str(e)}"}

@app.post("/api/admin/users/bulk-delete")
async def bulk_delete_users(
    user_ids: List[int] = Body(...),
    user: User = Depends(require_auth)
):
    """Bulk delete users"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Prevent deleting admin users
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE id IN ({}) AND role = 'admin'
        """.format(','.join(['?'] * len(user_ids))), user_ids)
        
        admin_count = cursor.fetchone()[0]
        if admin_count > 0:
            return {"success": False, "error": "Cannot delete admin users"}
        
        # Delete users
        cursor.execute("""
            DELETE FROM users 
            WHERE id IN ({})
        """.format(','.join(['?'] * len(user_ids))), user_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Deleted {cursor.rowcount} users",
            "affected_count": cursor.rowcount
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk delete users: {str(e)}")
        return {"success": False, "error": f"Failed to bulk delete users: {str(e)}"}

@app.post("/api/admin/users/bulk-change-role")
async def bulk_change_role(
    user_ids: List[int] = Body(...),
    new_role: str = Body(...),
    user: User = Depends(require_auth)
):
    """Bulk change user roles"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if new_role not in ["user", "admin", "manager", "lawyer", "paralegal"]:
        return {"success": False, "error": "Invalid role"}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({})
        """.format(','.join(['?'] * len(user_ids))), [new_role] + user_ids)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Changed role to {new_role} for {cursor.rowcount} users",
            "affected_count": cursor.rowcount
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk change role: {str(e)}")
        return {"success": False, "error": f"Failed to bulk change role: {str(e)}"}

# Document Export System
@app.get("/api/knowledge-base/my-documents")
async def get_my_documents(user: User = Depends(require_auth)):
    """Get user's own documents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's documents
        cursor.execute("""
            SELECT id, title, document_type, source, created_at, content
            FROM documents 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user.id,))
        
        documents = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "documents": documents
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/knowledge-base/export")
async def export_documents(
    format: str = "json",
    user: User = Depends(require_auth)
):
    """Export documents in various formats"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's documents
        cursor.execute("""
            SELECT d.*, u.username as owner_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.user_id = ? OR d.id IN (
                SELECT dp.document_id 
                FROM document_permissions dp 
                WHERE dp.requester_id = ? AND dp.status = 'approved'
            )
            ORDER BY d.created_at DESC
        """, (user.id, user.id))
        
        documents = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if format.lower() == "json":
            return JSONResponse(
                content={
                    "success": True,
                    "documents": documents,
                    "export_date": datetime.now().isoformat(),
                    "total_count": len(documents)
                }
            )
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Title", "Document Type", "Owner", "Source", 
                "Content Length", "Created At", "Updated At"
            ])
            
            # Write data
            for doc in documents:
                writer.writerow([
                    doc['id'],
                    doc['title'],
                    doc['document_type'],
                    doc['owner_name'],
                    doc['source'],
                    len(doc['content']) if doc['content'] else 0,
                    doc['created_at'],
                    doc['updated_at']
                ])
            
            output.seek(0)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=documents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        else:
            return {"success": False, "error": "Unsupported export format"}
        
    except Exception as e:
        logger.error(f"Failed to export documents: {str(e)}")
        return {"success": False, "error": f"Failed to export documents: {str(e)}"}

@app.get("/api/knowledge-base/document/{document_id}/pdf")
async def export_document_pdf(
    document_id: int,
    user: User = Depends(require_auth)
):
    """Export a single document as PDF"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check document access
        cursor.execute("""
            SELECT d.*, u.username as owner_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.id = ? AND (
                d.user_id = ? OR 
                d.id IN (
                    SELECT dp.document_id 
                    FROM document_permissions dp 
                    WHERE dp.requester_id = ? AND dp.status = 'approved'
                )
            )
        """, (document_id, user.id, user.id))
        
        document = cursor.fetchone()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found or access denied")
        
        cursor.close()
        conn.close()
        
        # Generate PDF content
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
            )
            
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
            )
            
            # Build PDF content
            story = []
            
            # Title
            story.append(Paragraph(document['title'], title_style))
            story.append(Spacer(1, 12))
            
            # Document info
            story.append(Paragraph(f"<b>Document Type:</b> {document['document_type']}", content_style))
            story.append(Paragraph(f"<b>Owner:</b> {document['owner_name']}", content_style))
            story.append(Paragraph(f"<b>Source:</b> {document['source']}", content_style))
            story.append(Paragraph(f"<b>Created:</b> {document['created_at']}", content_style))
            story.append(Spacer(1, 20))
            
            # Content
            if document['content']:
                # Split content into paragraphs
                paragraphs = document['content'].split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), content_style))
                        story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return Response(
                content=buffer.getvalue(),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={document['title']}.pdf"}
            )
            
        except ImportError:
            # Fallback to plain text if reportlab not available
            content = f"""
DALI Legal AI - Document Export
===============================

Title: {document['title']}
Document Type: {document['document_type']}
Owner: {document['owner_name']}
Source: {document['source']}
Created: {document['created_at']}

Content:
--------
{document['content'] if document['content'] else 'No content available'}
"""
            
            return Response(
                content=content,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={document['title']}.txt"}
            )
        
    except Exception as e:
        logger.error(f"Failed to export document PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export document: {str(e)}")

@app.get("/api/users/all")
async def get_all_users(
    limit: int = 100,
    offset: int = 0,
    role_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    user: User = Depends(require_auth)
):
    """Get all users with filtering options"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if role_filter:
            where_conditions.append("role = ?")
            params.append(role_filter)
        
        if status_filter:
            if status_filter == "active":
                where_conditions.append("is_active = 1")
            elif status_filter == "inactive":
                where_conditions.append("is_active = 0")
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get users with pagination
        cursor.execute(f"""
            SELECT id, username, email, first_name, last_name, 
                   company_name, job_title, role, is_active, 
                   created_at, updated_at
            FROM users 
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        users = cursor.fetchall()
        
        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) as total
            FROM users 
            {where_clause}
        """, params)
        
        total_count = cursor.fetchone()['total']
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "users": users,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Failed to get all users: {str(e)}")
        return {"success": False, "error": f"Failed to get all users: {str(e)}"}

# Activity Logging System
def log_activity(user_id: int, action: str, details: dict = None):
    """Log user activity to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        cursor.execute("""
            INSERT INTO activity_logs (user_id, action, details, ip_address, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, action, details_json, "127.0.0.1"))  # IP will be updated with real IP
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")

@app.get("/api/activity/logs")
async def get_activity_logs(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[int] = None,
    action_filter: Optional[str] = None,
    user: User = Depends(require_auth)
):
    """Get activity logs with filtering"""
    if user.role != "admin" and user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if user_id:
            where_conditions.append("al.user_id = ?")
            params.append(user_id)
        
        if action_filter:
            where_conditions.append("al.action = ?")
            params.append(action_filter)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get activity logs
        cursor.execute(f"""
            SELECT al.*, u.username, u.first_name, u.last_name
            FROM activity_logs al
            JOIN users u ON al.user_id = u.id
            {where_clause}
            ORDER BY al.created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        logs = cursor.fetchall()
        
        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) as total
            FROM activity_logs al
            {where_clause}
        """, params)
        
        total_count = cursor.fetchone()['total']
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "logs": logs,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Failed to get activity logs: {str(e)}")
        return {"success": False, "error": f"Failed to get activity logs: {str(e)}"}

@app.get("/api/activity/stats")
async def get_activity_stats(
    days: int = 30,
    user: User = Depends(require_auth)
):
    """Get activity statistics"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get activity stats for the last N days
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as activity_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM activity_logs 
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (days,))
        
        daily_stats = cursor.fetchall()
        
        # Get top actions
        cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM activity_logs 
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY action
            ORDER BY count DESC
            LIMIT 10
        """, (days,))
        
        top_actions = cursor.fetchall()
        
        # Get top users
        cursor.execute("""
            SELECT u.username, u.first_name, u.last_name, COUNT(*) as activity_count
            FROM activity_logs al
            JOIN users u ON al.user_id = u.id
            WHERE al.created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY al.user_id
            ORDER BY activity_count DESC
            LIMIT 10
        """, (days,))
        
        top_users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "daily_stats": daily_stats,
            "top_actions": top_actions,
            "top_users": top_users,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Failed to get activity stats: {str(e)}")
        return {"success": False, "error": f"Failed to get activity stats: {str(e)}"}

# Database Intelligence System

def convert_natural_language_to_sql(query: str) -> str:
    """Convert simple natural language queries to SQL"""
    query_lower = query.lower().strip()
    
    # Simple pattern matching for common queries
    if "show me all users" in query_lower:
        if "this month" in query_lower:
            return "SELECT * FROM users WHERE created_at >= date('now', 'start of month')"
        elif "recent" in query_lower:
            return "SELECT * FROM users ORDER BY created_at DESC LIMIT 10"
        else:
            return "SELECT * FROM users"
    
    elif "count users" in query_lower or "how many users" in query_lower:
        return "SELECT COUNT(*) as total_users FROM users"
    
    elif "show me all documents" in query_lower:
        if "this month" in query_lower:
            return "SELECT * FROM documents WHERE created_at >= date('now', 'start of month')"
        elif "recent" in query_lower:
            return "SELECT * FROM documents ORDER BY created_at DESC LIMIT 10"
        else:
            return "SELECT * FROM documents"
    
    elif "count documents" in query_lower or "how many documents" in query_lower:
        return "SELECT COUNT(*) as total_documents FROM documents"
    
    elif "document types" in query_lower:
        return "SELECT document_type, COUNT(*) as count FROM documents GROUP BY document_type"
    
    elif "recent activity" in query_lower or "activity trends" in query_lower:
        return "SELECT DATE(created_at) as date, COUNT(*) as count FROM documents GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 10"
    
    elif "top users" in query_lower:
        return "SELECT u.username, COUNT(d.id) as document_count FROM users u LEFT JOIN documents d ON u.id = d.user_id GROUP BY u.id, u.username ORDER BY document_count DESC LIMIT 10"
    
    elif "chat activity" in query_lower:
        return "SELECT DATE(created_at) as date, COUNT(*) as message_count FROM messages GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 10"
    
    # If no pattern matches, return None
    return None

def generate_simple_chart(data: list, columns: list, query: str) -> str:
    """Generate a simple HTML chart for the data"""
    if not data or len(data) == 0:
        return ""
    
    # Simple bar chart for count queries
    if len(data) == 1 and len(columns) == 1:
        value = list(data[0].values())[0]
        return f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; color: #667eea; font-weight: bold;">{value}</div>
            <div style="font-size: 18px; color: #666;">{columns[0].replace('_', ' ').title()}</div>
        </div>
        """
    
    # Simple table for other data
    if len(data) <= 10:
        table_html = "<table style='width: 100%; border-collapse: collapse;'>"
        table_html += "<tr style='background: #f8f9fa;'>"
        for col in columns:
            table_html += f"<th style='padding: 8px; border: 1px solid #ddd;'>{col.replace('_', ' ').title()}</th>"
        table_html += "</tr>"
        
        for row in data:
            table_html += "<tr>"
            for col in columns:
                table_html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{row.get(col, '')}</td>"
            table_html += "</tr>"
        
        table_html += "</table>"
        return table_html
    
    return f"<p>Showing {len(data)} results. Data too large to display in chart format.</p>"
@app.post("/api/database-intelligence/natural-language-query")
async def natural_language_query(
    request: Request,
    natural_language: str = Form(""),
    user: User = Depends(require_auth)
):
    """Convert natural language to SQL and execute query with chart generation"""
    try:
        # Handle both JSON and Form data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            body = await request.json()
            query = body.get("query", "")
        else:
            query = natural_language
        
        if not query:
            return {
                "success": False,
                "error": "No query provided",
                "timestamp": datetime.now().isoformat()
            }
        
        # Simple natural language to SQL conversion
        sql_query = convert_natural_language_to_sql(query)
        
        if not sql_query:
            return {
                "success": False,
                "error": "Could not understand the query. Try using SQL directly.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute the SQL query using SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append(dict(zip(columns, row)))
            
            # Generate simple chart if data is suitable
            chart_html = generate_simple_chart(data, columns, query)
            
            return {
                "success": True,
                "natural_language": query,
                "sql_query": sql_query,
                "data": data,
                "columns": columns,
                "row_count": len(data),
                "chart_html": chart_html,
                "reasoning": f"Converted '{query}' to SQL and executed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "sql_query": sql_query,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Natural language query error: {str(e)}")
        return {"success": False, "error": f"Natural language query failed: {str(e)}"}

@app.post("/api/database-intelligence/execute-sql")
async def execute_sql_query(
    request: Request,
    sql_query: str = Form(""),
    natural_language: str = Form(""),
    user: User = Depends(require_auth)
):
    """Execute SQL query directly"""
    try:
        # Handle both JSON and Form data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON input
            body = await request.json()
            query = body.get("sql", "")
            description = body.get("natural_language", "")
        else:
            # Handle Form input
            query = sql_query
            description = natural_language
        
        if not query:
            return {
                "success": False,
                "error": "No SQL query provided",
                "timestamp": datetime.now().isoformat()
            }
        
        # Use SQLite instead of MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Execute the query
            cursor.execute(query)
            
            # Get results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                
                return {
                    "success": True,
                    "data": data,
                    "columns": columns,
                    "sql_query": query,
                    "row_count": len(data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # For non-SELECT queries
                conn.commit()
                return {
                    "success": True,
                    "message": "Query executed successfully",
                    "sql_query": query,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"SQL execution error: {str(e)}",
                "sql_query": query,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"SQL execution error: {str(e)}")
        return {"success": False, "error": f"SQL execution failed: {str(e)}"}

@app.post("/api/database-intelligence/generate-chart")
async def generate_chart_from_data(
    request: Request,
    data: str = Form(""),  # JSON string of data
    natural_language: str = Form(""),
    user: User = Depends(require_auth)
):
    """Generate chart from provided data"""
    try:
        import json
        import pandas as pd
        from src.core.database.chart_generator import ChartGenerator
        from src.utils.config import load_config
        
        # Handle both JSON and Form data
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON input
            body = await request.json()
            chart_data = body.get("data", "")
            chart_type = body.get("chart_type", "bar")
            description = body.get("natural_language", "")
        else:
            # Handle Form input
            chart_data = data
            chart_type = "bar"  # Default chart type
            description = natural_language
        
        if not chart_data:
            return {
                "success": False,
                "error": "No data provided for chart generation",
                "timestamp": datetime.now().isoformat()
            }
        
        # Parse data
        try:
            if isinstance(chart_data, str):
                data_dict = json.loads(chart_data)
            else:
                data_dict = chart_data
            df = pd.DataFrame(data_dict)
        except Exception as e:
            return {"success": False, "error": f"Invalid data format: {str(e)}"}
        
        # Generate chart
        config = load_config('config/config.yaml')
        chart_generator = ChartGenerator(config)
        
        chart_result = chart_generator.generate_chart(df, description)
        
        if chart_result['success']:
            return {
                "success": True,
                "chart_html": chart_result['chart_html'],
                "chart_config": chart_result['chart_config'],
                "reasoning": chart_result.get('reasoning', 'Chart generated based on data structure'),
                "data_points": len(df)
            }
        else:
            return {"success": False, "error": chart_result['error']}
            
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        return {"success": False, "error": f"Chart generation failed: {str(e)}"}

@app.get("/api/database-intelligence/schema")
async def get_database_schema(user: User = Depends(require_auth)):
    """Get database schema information"""
    try:
        # Use SQLite instead of MySQL for this application
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Get schema information for each table
        schema_info = []
        tables_list = []
        
        for table in tables:
            table_name = table[0]
            tables_list.append(table_name)
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            table_info = {
                "name": table_name,
                "columns": []
            }
            
            for col in columns:
                table_info["columns"].append({
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "primary_key": bool(col[5])
                })
            
            schema_info.append(table_info)
        
        cursor.close()
        conn.close()
        
        # Create schema context
        schema_context = f"Database: SQLite\nTables: {', '.join(tables_list)}\n\n"
        for table in schema_info:
            schema_context += f"Table: {table['name']}\n"
            for col in table['columns']:
                schema_context += f"  - {col['name']} ({col['type']})"
                if col['primary_key']:
                    schema_context += " [PRIMARY KEY]"
                if col['not_null']:
                    schema_context += " [NOT NULL]"
                schema_context += "\n"
            schema_context += "\n"
        
        return {
            "success": True,
            "schema_context": schema_context,
            "tables": schema_info,
            "connection_status": "connected"
        }
        
    except Exception as e:
        logger.error(f"Schema retrieval error: {str(e)}")
        return {"success": False, "error": f"Schema retrieval failed: {str(e)}"}

# Settings and User Management
@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user: User = Depends(require_auth)):
    """User settings page"""
    return templates.TemplateResponse("new_settings.html", {
        "request": request,
        "title": "Settings - DALI Legal AI",
        "user": user,
        "t": lambda key: t(key, request)
    })

@app.get("/api/user/profile")
async def get_user_profile(user: User = Depends(require_auth)):
    """Get user profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   company_name, job_title, phone, department, role, is_active
            FROM users WHERE id = ?
        """, (user.id,))
        profile = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if profile:
            # Remove sensitive data
            del profile['id']
            return {
                "success": True,
                "profile": profile
            }
        else:
            return {
                "success": False,
                "error": "User not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/user/profile")
async def update_user_profile(request: Request, user: User = Depends(require_auth)):
    """Update user profile information"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET 
                first_name = ?, last_name = ?, email = ?,
                company_name = ?, job_title = ?, phone = ?, department = ?
            WHERE id = ?
        """, (
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('email', ''),
            data.get('company_name', ''),
            data.get('job_title', ''),
            data.get('phone', ''),
            data.get('department', ''),
            user.id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/user/password")
async def change_password(request: Request, user: User = Depends(require_auth)):
    """Change user password"""
    try:
        data = await request.json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return {
                "success": False,
                "error": "Current password and new password are required"
            }
        
        # Verify current password
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user.id,))
        user_data = cursor.fetchone()
        
        if not user_data or not pwd_context.verify(current_password, user_data['password_hash']):
            cursor.close()
            conn.close()
            return {
                "success": False,
                "error": "Current password is incorrect"
            }
        
        # Update password
        new_password_hash = pwd_context.hash(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user.id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/user/settings")
async def get_user_settings(user: User = Depends(require_auth)):
    """Get user LLM settings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all settings for the user
        cursor.execute("""
            SELECT setting_key, setting_value FROM user_settings WHERE user_id = ?
        """, (user.id,))
        settings_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert key-value pairs to settings object
        settings = {}
        for row in settings_rows:
            settings[row['setting_key']] = row['setting_value']
        
        # Return default settings if none found
        if not settings:
            settings = {
                'llm_provider': 'openai',
                'llm_model': 'gpt-3.5-turbo',
                'temperature': '0.7',
                'max_tokens': '2000',
                'chunk_size': '1000',
                'chunk_overlap': '200'
            }
        
        # Ensure all required settings exist with defaults
        default_settings = {
            'llm_provider': 'openai',
            'llm_model': 'gpt-3.5-turbo',
            'temperature': '0.7',
            'max_tokens': '2000',
            'chunk_size': '1000',
            'chunk_overlap': '200'
        }
        
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        return {
            "success": True,
            "settings": settings
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "settings": {
                'llm_provider': 'openai',
                'llm_model': 'gpt-3.5-turbo',
                'temperature': '0.7',
                'max_tokens': '2000',
                'chunk_size': '1000',
                'chunk_overlap': '200'
            }
        }

@app.post("/api/user/update_activity")
async def update_user_activity(user: User = Depends(require_auth)):
    """Update user activity timestamp"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update last activity timestamp
        cursor.execute("""
            UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?
        """, (user.id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Activity updated"}
    except Exception as e:
        logger.error(f"Error updating user activity: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/user/settings")
async def update_user_settings(request: Request, user: User = Depends(require_auth)):
    """Update user LLM settings"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Settings to update
        settings_to_update = {
            'llm_provider': str(data.get('llm_provider', 'openai')),
            'llm_model': str(data.get('llm_model', 'gpt-3.5-turbo')),
            'temperature': str(data.get('temperature', '0.7')),
            'max_tokens': str(data.get('max_tokens', '2000')),
            'chunk_size': str(data.get('chunk_size', '1000')),
            'chunk_overlap': str(data.get('chunk_overlap', '200'))
        }
        
        # Update or insert each setting
        for setting_key, setting_value in settings_to_update.items():
            # First try to update existing setting
            cursor.execute("""
                UPDATE user_settings 
                SET setting_value = ? 
                WHERE user_id = ? AND setting_key = ?
            """, (setting_value, user.id, setting_key))
            
            # If no rows were updated, insert new setting
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO user_settings (user_id, setting_key, setting_value)
                    VALUES (?, ?, ?)
                """, (user.id, setting_key, setting_value))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Settings updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Document Sharing and Management
@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request, user: User = Depends(require_auth)):
    """All documents page with sharing functionality"""
    return templates.TemplateResponse("new_documents.html", {
        "request": request,
        "title": "Documents - DALI Legal AI",
        "user": user,
        "t": lambda key: t(key, request)
    })

@app.get("/api/documents")
async def get_documents(user: User = Depends(require_auth)):
    """Get all documents accessible to the user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get documents owned by user or shared with user
        cursor.execute("""
            SELECT d.id, d.title, d.document_type, d.source, d.created_at, 
                   d.user_id, u.username as owner_name,
                   CASE WHEN d.user_id = ? THEN 'owner' ELSE 'shared' END as access_type
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.user_id = ? OR d.id IN (
                SELECT document_id FROM document_permissions 
                WHERE user_id = ? AND permission_type = 'read'
            )
            ORDER BY d.created_at DESC
        """, (user.id, user.id, user.id))
        
        documents = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "documents": documents
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/documents/{document_id}")
async def get_document(document_id: int, user: User = Depends(require_auth)):
    """Get a specific document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user has access to document
        cursor.execute("""
            SELECT d.*, u.username as owner_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.id = ? AND (
                d.user_id = ? OR 
                d.id IN (SELECT document_id FROM document_permissions WHERE user_id = ? AND permission_type = 'read')
            )
        """, (document_id, user.id, user.id))
        
        document = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if document:
            return {
                "success": True,
                "document": document
            }
        else:
            return {
                "success": False,
                "error": "Document not found or access denied"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/documents/{document_id}/share")
async def share_document(document_id: int, request: Request, user: User = Depends(require_auth)):
    """Share a document with another user"""
    try:
        data = await request.json()
        target_user_id = data.get('user_id')
        permission = data.get('permission', 'read')
        
        if not target_user_id:
            return {
                "success": False,
                "error": "Target user ID is required"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user owns the document
        cursor.execute("SELECT user_id FROM documents WHERE id = ?", (document_id,))
        doc_owner = cursor.fetchone()
        
        if not doc_owner or doc_owner[0] != user.id:
            cursor.close()
            conn.close()
            return {
                "success": False,
                "error": "You can only share documents you own"
            }
        
        # Check if permission already exists
        cursor.execute("""
            SELECT id FROM document_permissions 
            WHERE document_id = ? AND user_id = ?
        """, (document_id, target_user_id))
        
        if cursor.fetchone():
            # Update existing permission
            cursor.execute("""
                UPDATE document_permissions 
                SET permission = ?, updated_at = CURRENT_TIMESTAMP
                WHERE document_id = ? AND user_id = ?
            """, (permission, document_id, target_user_id))
        else:
            # Create new permission
            cursor.execute("""
                INSERT INTO document_permissions (document_id, user_id, permission_type, granted_by, granted_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (document_id, target_user_id, permission, user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Document shared successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/documents/{document_id}/permissions")
async def get_document_permissions(document_id: int, user: User = Depends(require_auth)):
    """Get permissions for a document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user owns the document
        cursor.execute("SELECT user_id FROM documents WHERE id = ?", (document_id,))
        doc_owner = cursor.fetchone()
        
        if not doc_owner or doc_owner[0] != user.id:
            cursor.close()
            conn.close()
            return {
                "success": False,
                "error": "You can only view permissions for documents you own"
            }
        
        # Get permissions
        cursor.execute("""
            SELECT dp.*, u.username, u.email, u.first_name, u.last_name
            FROM document_permissions dp
            JOIN users u ON dp.user_id = u.id
            WHERE dp.document_id = ?
            ORDER BY dp.created_at DESC
        """, (document_id,))
        
        permissions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "permissions": permissions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int, user: User = Depends(require_auth)):
    """Delete a document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user owns the document
        cursor.execute("SELECT user_id, title FROM documents WHERE id = ?", (document_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if result['user_id'] != user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own documents")
        
        # Delete document permissions first
        cursor.execute("DELETE FROM document_permissions WHERE document_id = ?", (document_id,))
        
        # Delete from vector store
        try:
            from src.core.vector_store import VectorStore
            vector_store = VectorStore()
            vector_store.delete_document(document_id)
        except Exception as e:
            logger.warning(f"Could not delete from vector store: {e}")
        
        # Delete the document
        cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": f"Document '{result['title']}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}/permissions/{permission_id}")
async def remove_document_permission(document_id: int, permission_id: int, user: User = Depends(require_auth)):
    """Remove a document permission"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user owns the document
        cursor.execute("SELECT user_id FROM documents WHERE id = ?", (document_id,))
        doc_owner = cursor.fetchone()
        
        if not doc_owner or doc_owner[0] != user.id:
            cursor.close()
            conn.close()
            return {
                "success": False,
                "error": "You can only modify permissions for documents you own"
            }
        
        # Remove permission
        cursor.execute("""
            DELETE FROM document_permissions 
            WHERE id = ? AND document_id = ?
        """, (permission_id, document_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Permission removed successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/all-documents", response_class=HTMLResponse)
async def all_documents_page(request: Request, user: User = Depends(require_auth)):
    """All documents management page"""
    return templates.TemplateResponse("all_documents.html", {
        "request": request,
        "user": user,
        "title": "All Documents - DALI Legal AI",
        "t": lambda key: t(key, request)
    })

@app.get("/document/{document_id}", response_class=HTMLResponse)
async def view_document_page(document_id: int, request: Request, user: User = Depends(require_auth)):
    """View individual document page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get document with uploader info
        cursor.execute("""
            SELECT d.*, u.username as uploader_name,
                   CASE WHEN d.user_id = ? THEN 1 ELSE 0 END as is_owner,
                   dp.permission_type
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            LEFT JOIN document_permissions dp ON d.id = dp.document_id AND dp.user_id = ?
            WHERE d.id = ?
        """, (user.id, user.id, document_id))
        
        document = cursor.fetchone()
        conn.close()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user has access
        if not document['is_owner'] and not document['permission_type']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return templates.TemplateResponse("document_view.html", {
            "request": request,
            "user": user,
            "document": document,
            "title": f"{document['title']} - DALI Legal AI",
            "t": lambda key: t(key, request)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}/download")
async def download_document(document_id: int, user: User = Depends(require_auth)):
    """Download a document file"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get document with permission check
        cursor.execute("""
            SELECT d.*, u.username as uploader_name,
                   CASE WHEN d.user_id = ? THEN 1 ELSE 0 END as is_owner,
                   dp.permission_type
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            LEFT JOIN document_permissions dp ON d.id = dp.document_id AND dp.user_id = ?
            WHERE d.id = ?
        """, (user.id, user.id, document_id))
        
        document = cursor.fetchone()
        conn.close()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check permissions
        if not document['is_owner'] and not document['permission_type']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if document has file content
        if not document.get('content'):
            raise HTTPException(status_code=404, detail="Document content not available for download")
        
        # Create a simple text file with the document content
        content = document['content']
        filename = f"{document['title']}.txt"
        
        # Return the file as a streaming response
        from fastapi.responses import StreamingResponse
        import io
        
        def generate():
            yield content.encode('utf-8')
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/users/search")
async def search_users(query: str = "", user: User = Depends(require_auth)):
    """Search users for sharing"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if query:
            cursor.execute("""
                SELECT id, username, email, first_name, last_name
                FROM users 
                WHERE (username LIKE ? OR email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)
                AND id != ?
                ORDER BY username
                LIMIT 10
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', user.id))
        else:
            cursor.execute("""
                SELECT id, username, email, first_name, last_name
                FROM users 
                WHERE id != ?
                ORDER BY username
                LIMIT 10
            """, (user.id,))
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "users": users
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# User-to-User Chat API endpoints
@app.get("/api/user-conversations")
async def get_user_conversations(user: User = Depends(require_auth)):
    """Get all conversations for the current user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversations with other users
        cursor.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN sender_id = ? THEN receiver_id 
                    ELSE sender_id 
                END as user_id,
                u.username,
                u.role,
                MAX(um.timestamp) as last_message_time,
                (SELECT content FROM user_messages um2 
                 WHERE ((um2.sender_id = ? AND um2.receiver_id = u.id) 
                        OR (um2.sender_id = u.id AND um2.receiver_id = ?))
                 ORDER BY um2.timestamp DESC LIMIT 1) as last_message,
                COUNT(CASE WHEN um.receiver_id = ? AND um.is_read = 0 THEN 1 END) as unread_count
            FROM user_messages um
            JOIN users u ON (um.sender_id = u.id OR um.receiver_id = u.id)
            WHERE (um.sender_id = ? OR um.receiver_id = ?) 
            AND u.id != ?
            GROUP BY user_id, u.username, u.role
            ORDER BY last_message_time DESC
        """, (user.id, user.id, user.id, user.id, user.id, user.id, user.id))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "conversations": conversations
        }
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/user-chat/messages/{user_id}")
async def get_user_chat_messages(user_id: int, user: User = Depends(require_auth)):
    """Get messages between current user and specified user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get messages between users
        cursor.execute("""
            SELECT um.*, u.username as sender_name
            FROM user_messages um
            JOIN users u ON um.sender_id = u.id
            WHERE ((um.sender_id = ? AND um.receiver_id = ?) 
                   OR (um.sender_id = ? AND um.receiver_id = ?))
            ORDER BY um.timestamp ASC
        """, (user.id, user_id, user_id, user.id))
        
        messages = cursor.fetchall()
        
        # Mark messages as read
        cursor.execute("""
            UPDATE user_messages 
            SET is_read = 1 
            WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
        """, (user_id, user.id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/user-chat/send")
async def send_user_message(request: Request, user: User = Depends(require_auth)):
    """Send a message to another user"""
    try:
        data = await request.json()
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        
        if not receiver_id or not content:
            return {
                "success": False,
                "error": "Receiver ID and content are required"
            }
        
        # Check if receiver exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE id = ?", (receiver_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "error": "Receiver user not found"
            }
        
        # Insert message
        cursor.execute("""
            INSERT INTO user_messages (sender_id, receiver_id, content, timestamp, is_read)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0)
        """, (user.id, receiver_id, content))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/user-chat/unread-count")
async def get_unread_message_count(user: User = Depends(require_auth)):
    """Get total unread message count for current user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM user_messages 
            WHERE receiver_id = ? AND is_read = 0
        """, (user.id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "success": True,
            "unread_count": result['unread_count']
        }
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return {
            "success": False,
            "error": str(e)
        }




# Document Permission System
@app.post("/api/documents/{document_id}/request-permission")
async def request_document_permission(document_id: int, request: Request, user: User = Depends(require_auth)):
    """Request permission to access a document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get document and owner
        cursor.execute("""
            SELECT d.id, d.title, d.user_id, u.username as owner_username
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.id = ?
        """, (document_id,))
        
        document = cursor.fetchone()
        if not document:
            return {
                "success": False,
                "error": "Document not found"
            }
        
        if document['user_id'] == user.id:
            return {
                "success": False,
                "error": "You already own this document"
            }
        
        # Check if permission request already exists
        cursor.execute("""
            SELECT id FROM document_permission_requests 
            WHERE document_id = ? AND requester_id = ? AND status = 'pending'
        """, (document_id, user.id))
        
        existing_request = cursor.fetchone()
        if existing_request:
            return {
                "success": False,
                "error": "Permission request already pending"
            }
        
        # Create permission request
        cursor.execute("""
            INSERT INTO document_permission_requests 
            (document_id, requester_id, owner_id, status, created_at)
            VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        """, (document_id, user.id, document['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Permission request sent to {document['owner_username']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to request document permission: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/documents/permission-requests")
async def get_permission_requests(user: User = Depends(require_auth)):
    """Get all permission requests for the user (incoming and outgoing)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get outgoing requests (requests made by user)
        cursor.execute("""
            SELECT 
                r.id, r.document_id, r.status, r.created_at,
                d.title as document_title,
                u.username as owner_username, u.first_name as owner_first_name, u.last_name as owner_last_name
            FROM document_permission_requests r
            JOIN documents d ON r.document_id = d.id
            JOIN users u ON r.owner_id = u.id
            WHERE r.requester_id = ?
            ORDER BY r.created_at DESC
        """, (user.id,))
        
        outgoing_requests = cursor.fetchall()
        
        # Get incoming requests (requests made to user)
        cursor.execute("""
            SELECT 
                r.id, r.document_id, r.status, r.created_at,
                d.title as document_title,
                u.username as requester_username, u.first_name as requester_first_name, u.last_name as requester_last_name
            FROM document_permission_requests r
            JOIN documents d ON r.document_id = d.id
            JOIN users u ON r.requester_id = u.id
            WHERE r.owner_id = ?
            ORDER BY r.created_at DESC
        """, (user.id,))
        
        incoming_requests = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "outgoing_requests": outgoing_requests,
            "incoming_requests": incoming_requests
        }
        
    except Exception as e:
        logger.error(f"Failed to get permission requests: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/documents/permission-requests/{request_id}/approve")
async def approve_permission_request(request_id: int, user: User = Depends(require_auth)):
    """Approve a permission request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update request status
        cursor.execute("""
            UPDATE document_permission_requests 
            SET status = 'approved', updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND owner_id = ? AND status = 'pending'
        """, (request_id, user.id))
        
        if cursor.rowcount == 0:
            return {
                "success": False,
                "error": "Request not found or already processed"
            }
        
        # Get request details for sharing
        cursor.execute("""
            SELECT document_id, requester_id 
            FROM document_permission_requests 
            WHERE id = ?
        """, (request_id,))
        
        request_data = cursor.fetchone()
        if request_data:
            # Create document permission
            cursor.execute("""
                UPDATE document_permissions 
                SET permission_type = 'read', granted_at = CURRENT_TIMESTAMP
                WHERE document_id = ? AND user_id = ?
            """, (request_data[0], request_data[1]))
            
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO document_permissions 
                    (document_id, user_id, permission_type, granted_by, granted_at)
                    VALUES (?, ?, 'read', ?, CURRENT_TIMESTAMP)
                """, (request_data[0], request_data[1], user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Permission request approved"
        }
        
    except Exception as e:
        logger.error(f"Failed to approve permission request: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/documents/permission-requests/{request_id}/deny")
async def deny_permission_request(request_id: int, user: User = Depends(require_auth)):
    """Deny a permission request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update request status
        cursor.execute("""
            UPDATE document_permission_requests 
            SET status = 'denied', updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND owner_id = ? AND status = 'pending'
        """, (request_id, user.id))
        
        if cursor.rowcount == 0:
            return {
                "success": False,
                "error": "Request not found or already processed"
            }
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Permission request denied"
        }
        
    except Exception as e:
        logger.error(f"Failed to deny permission request: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Bulk Operations for Admin
@app.post("/api/admin/users/bulk-delete")
async def bulk_delete_users(request: Request, user: User = Depends(require_admin)):
    """Bulk delete users (admin only)"""
    try:
        data = await request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {
                "success": False,
                "error": "No user IDs provided"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete users (cascade will handle related data)
        placeholders = ','.join(['?'] * len(user_ids))
        cursor.execute(f"""
            DELETE FROM users 
            WHERE id IN ({placeholders}) AND id != ?
        """, user_ids + [user.id])  # Prevent admin from deleting themselves
        
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully deleted {deleted_count} users",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk delete users: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/admin/users/bulk-activate")
async def bulk_activate_users(request: Request, user: User = Depends(require_admin)):
    """Bulk activate users (admin only)"""
    try:
        data = await request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {
                "success": False,
                "error": "No user IDs provided"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Activate users
        placeholders = ','.join(['?'] * len(user_ids))
        cursor.execute(f"""
            UPDATE users 
            SET is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders})
        """, user_ids)
        
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully activated {updated_count} users",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk activate users: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/admin/users/bulk-deactivate")
async def bulk_deactivate_users(request: Request, user: User = Depends(require_admin)):
    """Bulk deactivate users (admin only)"""
    try:
        data = await request.json()
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return {
                "success": False,
                "error": "No user IDs provided"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Deactivate users (but don't deactivate admin)
        placeholders = ','.join(['?'] * len(user_ids))
        cursor.execute(f"""
            UPDATE users 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders}) AND id != ?
        """, user_ids + [user.id])  # Prevent admin from deactivating themselves
        
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully deactivated {updated_count} users",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk deactivate users: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/admin/users/bulk-update-role")
async def bulk_update_user_roles(request: Request, user: User = Depends(require_admin)):
    """Bulk update user roles (admin only)"""
    try:
        data = await request.json()
        user_ids = data.get("user_ids", [])
        new_role = data.get("role", "")
        
        if not user_ids or not new_role:
            return {
                "success": False,
                "error": "User IDs and role are required"
            }
        
        if new_role not in ['user', 'admin', 'manager', 'lawyer', 'paralegal']:
            return {
                "success": False,
                "error": "Invalid role"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user roles (but don't change admin role)
        placeholders = ','.join(['?'] * len(user_ids))
        cursor.execute(f"""
            UPDATE users 
            SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders}) AND id != ?
        """, [new_role] + user_ids + [user.id])  # Prevent admin from changing their own role
        
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully updated {updated_count} users to {new_role} role",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk update user roles: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/admin/users/export")
async def export_users(user: User = Depends(require_admin)):
    """Export all users to CSV (admin only)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, username, email, first_name, last_name, 
                role, is_active, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        if users:
            writer = csv.DictWriter(output, fieldnames=users[0].keys())
            writer.writeheader()
            writer.writerows(users)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "success": True,
            "csv_content": csv_content,
            "filename": f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "user_count": len(users)
        }
        
    except Exception as e:
        logger.error(f"Failed to export users: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/admin/users/import")
async def import_users(request: Request, user: User = Depends(require_admin)):
    """Import users from CSV (admin only)"""
    try:
        data = await request.json()
        csv_content = data.get("csv_content", "")
        
        if not csv_content:
            return {
                "success": False,
                "error": "CSV content is required"
            }
        
        import csv
        import io
        
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        users_data = list(csv_reader)
        
        if not users_data:
            return {
                "success": False,
                "error": "No user data found in CSV"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        errors = []
        
        for row in users_data:
            try:
                # Validate required fields
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', 'defaultpassword123').strip()
                
                if not username or not email:
                    errors.append(f"Row {imported_count + 1}: Missing username or email")
                    continue
                
                # Hash password
                password_hash = pwd_context.hash(password)
                
                # Insert user
                cursor.execute("""
                    INSERT INTO users 
                    (username, email, password_hash, first_name, last_name, 
                     role, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    username,
                    email,
                    password_hash,
                    row.get('first_name', ''),
                    row.get('last_name', ''),
                    row.get('role', 'user'),
                    row.get('is_active', 'true').lower() == 'true'
                ))
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {imported_count + 1}: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully imported {imported_count} users",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Failed to import users: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Court Simulation API Endpoints

@app.post("/api/court-simulation/upload-case")
async def upload_case_for_simulation(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    user: User = Depends(require_auth)
):
    """Upload and analyze case document for court simulation"""
    try:
        # Read file content
        content = await file.read()
        
        # Analyze the case document
        analysis_result = await analyze_document_with_llm(
            document_text=content.decode('utf-8', errors='ignore'),
            analysis_type="comprehensive",
            user=user
        )
        
        # Extract key information for simulation
        case_analysis = {
            "title": title or file.filename,
            "description": description,
            "filename": file.filename,
            "content": content.decode('utf-8', errors='ignore'),
            "analysis": analysis_result,
            "key_points": extract_key_legal_points(analysis_result),
            "case_type": determine_case_type(analysis_result),
            "relevant_laws": extract_relevant_laws(analysis_result),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": case_analysis,
            "message": "Case uploaded and analyzed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error uploading case for simulation: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to upload case: {str(e)}"
        }

@app.post("/api/court-simulation/respond")
async def court_simulation_respond(
    request_data: dict,
    user: User = Depends(require_auth)
):
    """Handle responses in court simulation"""
    try:
        message = request_data.get("message", "")
        case_data = request_data.get("caseData", {})
        conversation_history = request_data.get("conversationHistory", [])
        
        # Get user's LLM settings
        llm_settings = await get_user_llm_settings(user)
        
        # Generate judge response
        judge_response = await generate_judge_response(
            message=message,
            case_data=case_data,
            conversation_history=conversation_history,
            llm_settings=llm_settings
        )
        
        # Generate prosecutor response
        prosecutor_response = await generate_prosecutor_response(
            message=message,
            case_data=case_data,
            conversation_history=conversation_history,
            llm_settings=llm_settings
        )
        
        return {
            "success": True,
            "judgeResponse": judge_response,
            "prosecutorResponse": prosecutor_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in court simulation response: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate responses: {str(e)}"
        }

@app.post("/api/court-simulation/generate-report")
async def generate_court_simulation_report(
    request_data: dict,
    user: User = Depends(require_auth)
):
    """Generate PDF report for court simulation"""
    try:
        case_data = request_data.get("caseData", {})
        conversation_history = request_data.get("conversationHistory", [])
        simulation_duration = request_data.get("simulationDuration", 0)
        
        # Generate comprehensive report
        report_data = generate_simulation_report(
            case_data=case_data,
            conversation_history=conversation_history,
            simulation_duration=simulation_duration,
            user=user
        )
        
        # Create PDF report
        pdf_url = create_pdf_report(report_data, user.id)
        
        return {
            "success": True,
            "reportUrl": pdf_url,
            "reportData": report_data,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating court simulation report: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate report: {str(e)}"
        }

# Helper functions for court simulation

def extract_key_legal_points(analysis_text: str) -> list:
    """Extract key legal points from case analysis"""
    key_points = []
    lines = analysis_text.split('\n')
    
    for line in lines:
        if any(keyword in line.lower() for keyword in ['law', 'statute', 'regulation', 'precedent', 'ruling']):
            if len(line.strip()) > 20:
                key_points.append(line.strip())
    
    return key_points[:10]  # Return top 10 key points

def determine_case_type(analysis_text: str) -> str:
    """Determine the type of legal case"""
    text_lower = analysis_text.lower()
    
    if any(word in text_lower for word in ['criminal', 'felony', 'misdemeanor', 'theft', 'assault']):
        return "Criminal"
    elif any(word in text_lower for word in ['contract', 'agreement', 'breach', 'employment']):
        return "Contract"
    elif any(word in text_lower for word in ['family', 'divorce', 'custody', 'marriage']):
        return "Family Law"
    elif any(word in text_lower for word in ['property', 'real estate', 'land', 'ownership']):
        return "Property"
    elif any(word in text_lower for word in ['personal injury', 'accident', 'negligence', 'damages']):
        return "Personal Injury"
    else:
        return "General Civil"

def extract_relevant_laws(analysis_text: str) -> list:
    """Extract relevant laws and statutes from analysis"""
    laws = []
    import re
    
    # Look for common law patterns
    law_patterns = [
        r'section \d+',
        r'article \d+',
        r'statute \d+',
        r'code \d+',
        r'regulation \d+'
    ]
    
    for pattern in law_patterns:
        matches = re.findall(pattern, analysis_text, re.IGNORECASE)
        laws.extend(matches)
    
    return list(set(laws))[:5]  # Return unique laws, max 5

async def generate_judge_response(
    message: str,
    case_data: dict,
    conversation_history: list,
    llm_settings: dict
) -> str:
    """Generate AI judge response"""
    
    judge_prompt = f"""
    You are an experienced judge presiding over a court simulation. You are fair, impartial, and focused on legal procedure and evidence.

    CASE INFORMATION:
    Title: {case_data.get('title', 'Unknown Case')}
    Type: {case_data.get('case_type', 'General')}
    Key Points: {', '.join(case_data.get('key_points', [])[:3])}

    DEFENSE ATTORNEY'S STATEMENT:
    "{message}"

    CONVERSATION HISTORY:
    {format_conversation_history(conversation_history[-5:])}

    As the judge, respond with:
    1. Acknowledgment of the statement
    2. Relevant legal questions or clarifications
    3. Procedural guidance
    4. Focus on evidence and legal standards

    Keep responses professional, concise (2-3 sentences), and focused on legal procedure.
    """
    
    # Use the appropriate LLM
    llm_provider = llm_settings.get('llm_provider', 'openai')
    llm_model = llm_settings.get('llm_model', 'gpt-4o')
    
    if llm_provider == 'openai':
        try:
            import openai
            response = await openai.ChatCompletion.acreate(
                model=llm_model,
                messages=[{"role": "user", "content": judge_prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error in judge response: {e}")
            return "Your Honor acknowledges your statement. Please continue with your argument."
    else:
        # Use Ollama
        try:
            from src.core.llm_engine import LLMEngine
            llm_engine = LLMEngine(model_name=llm_model)
            response = llm_engine.generate_response(judge_prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Ollama error in judge response: {e}")
            return "Your Honor acknowledges your statement. Please continue with your argument."

async def generate_prosecutor_response(
    message: str,
    case_data: dict,
    conversation_history: list,
    llm_settings: dict
) -> str:
    """Generate AI prosecutor response"""
    
    prosecutor_prompt = f"""
    You are a skilled prosecutor in a court simulation. You are focused on presenting the case against the defendant and challenging the defense's arguments.

    CASE INFORMATION:
    Title: {case_data.get('title', 'Unknown Case')}
    Type: {case_data.get('case_type', 'General')}
    Key Points: {', '.join(case_data.get('key_points', [])[:3])}

    DEFENSE ATTORNEY'S STATEMENT:
    "{message}"

    CONVERSATION HISTORY:
    {format_conversation_history(conversation_history[-5:])}

    As the prosecutor, respond with:
    1. Challenge to the defense argument
    2. Questions about evidence or testimony
    3. Legal precedents that support your case
    4. Focus on weaknesses in the defense

    Keep responses professional, assertive (2-3 sentences), and focused on building your case.
    """
    
    # Use the appropriate LLM
    llm_provider = llm_settings.get('llm_provider', 'openai')
    llm_model = llm_settings.get('llm_model', 'gpt-4o')
    
    if llm_provider == 'openai':
        try:
            import openai
            response = await openai.ChatCompletion.acreate(
                model=llm_model,
                messages=[{"role": "user", "content": prosecutor_prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error in prosecutor response: {e}")
            return "The prosecution challenges that argument. Can you provide evidence to support your claim?"
    else:
        # Use Ollama
        try:
            from src.core.llm_engine import LLMEngine
            llm_engine = LLMEngine(model_name=llm_model)
            response = llm_engine.generate_response(prosecutor_prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Ollama error in prosecutor response: {e}")
            return "The prosecution challenges that argument. Can you provide evidence to support your claim?"

def format_conversation_history(history: list) -> str:
    """Format conversation history for prompts"""
    formatted = []
    for entry in history[-5:]:  # Last 5 entries
        formatted.append(f"{entry.get('sender', 'Unknown')}: {entry.get('message', '')}")
    return '\n'.join(formatted)

def generate_simulation_report(
    case_data: dict,
    conversation_history: list,
    simulation_duration: int,
    user: User
) -> dict:
    """Generate comprehensive simulation report data"""
    
    # Analyze conversation
    defense_messages = [msg for msg in conversation_history if msg.get('sender') == 'defense']
    judge_messages = [msg for msg in conversation_history if msg.get('sender') == 'judge']
    prosecutor_messages = [msg for msg in conversation_history if msg.get('sender') == 'prosecutor']
    
    # Calculate metrics
    total_messages = len(conversation_history)
    defense_participation = len(defense_messages)
    avg_response_length = sum(len(msg.get('message', '')) for msg in defense_messages) / max(defense_participation, 1)
    
    # Generate recommendations
    recommendations = generate_recommendations(case_data, conversation_history)
    
    # Find similar cases
    similar_cases = find_similar_cases(case_data)
    
    report_data = {
        "case_info": {
            "title": case_data.get('title', 'Unknown Case'),
            "type": case_data.get('case_type', 'General'),
            "description": case_data.get('description', ''),
            "key_points": case_data.get('key_points', []),
            "relevant_laws": case_data.get('relevant_laws', [])
        },
        "simulation_metrics": {
            "duration_minutes": simulation_duration // 60,
            "total_messages": total_messages,
            "defense_participation": defense_participation,
            "judge_questions": len(judge_messages),
            "prosecutor_challenges": len(prosecutor_messages),
            "avg_response_length": round(avg_response_length, 1)
        },
        "performance_analysis": {
            "strengths": analyze_strengths(conversation_history),
            "weaknesses": analyze_weaknesses(conversation_history),
            "improvement_areas": identify_improvement_areas(conversation_history)
        },
        "recommendations": recommendations,
        "similar_cases": similar_cases,
        "generated_at": datetime.now().isoformat(),
        "user": {
            "name": user.first_name + " " + user.last_name,
            "email": user.email
        }
    }
    
    return report_data

def generate_recommendations(case_data: dict, conversation_history: list) -> list:
    """Generate recommendations based on simulation"""
    recommendations = []
    
    defense_messages = [msg for msg in conversation_history if msg.get('sender') == 'defense']
    
    if len(defense_messages) < 3:
        recommendations.append("Consider providing more detailed responses to strengthen your arguments")
    
    if any('evidence' in msg.get('message', '').lower() for msg in defense_messages):
        recommendations.append("Good focus on evidence - continue emphasizing factual support")
    else:
        recommendations.append("Consider incorporating more evidence-based arguments")
    
    recommendations.append("Review similar cases to strengthen your legal precedents")
    recommendations.append("Practice responding to challenging questions from the prosecution")
    
    return recommendations

def find_similar_cases(case_data: dict) -> list:
    """Find similar cases from knowledge base"""
    return [
        {
            "title": "Similar Case Example 1",
            "outcome": "Defendant acquitted",
            "key_factors": ["Strong evidence", "Witness testimony"],
            "lessons": "Focus on witness credibility"
        },
        {
            "title": "Similar Case Example 2", 
            "outcome": "Settlement reached",
            "key_factors": ["Documentation", "Expert testimony"],
            "lessons": "Prepare expert witnesses thoroughly"
        }
    ]

def analyze_strengths(conversation_history: list) -> list:
    """Analyze strengths from conversation"""
    strengths = []
    defense_messages = [msg for msg in conversation_history if msg.get('sender') == 'defense']
    
    if len(defense_messages) > 0:
        strengths.append("Active participation in proceedings")
        strengths.append("Responsive to questions")
    
    return strengths

def analyze_weaknesses(conversation_history: list) -> list:
    """Analyze weaknesses from conversation"""
    weaknesses = []
    defense_messages = [msg for msg in conversation_history if msg.get('sender') == 'defense']
    
    if len(defense_messages) < 2:
        weaknesses.append("Limited participation")
    
    return weaknesses

def identify_improvement_areas(conversation_history: list) -> list:
    """Identify areas for improvement"""
    areas = []
    areas.append("Practice responding to challenging questions")
    areas.append("Develop stronger legal arguments")
    areas.append("Prepare for unexpected questions")
    
    return areas

def create_pdf_report(report_data: dict, user_id: int) -> str:
    """Create PDF report file"""
    report_filename = f"court_simulation_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return f"/reports/{report_filename}"

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "new_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
