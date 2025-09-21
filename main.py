"""
DALI Legal AI - Enhanced Edition with Database Intelligence & Web Scraping
Main FastAPI application
"""

import uvicorn
import os
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import bcrypt
import jwt
import json

# Templates for enhanced dashboard
templates = Jinja2Templates(directory="templates")

# Authentication models
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

# Import your existing web application
from src.web.app import app as existing_app

# Import new enhanced API routes
from src.api.routes.knowledge_base import router as kb_router
from src.api.routes.web_scraping import router as scraping_router
from src.api.routes.admin import router as admin_router

# Create enhanced FastAPI app by extending the existing one
app = existing_app

# Add new API routes to the existing app
app.include_router(kb_router)
app.include_router(scraping_router)
app.include_router(admin_router)

# Ensure API documentation is accessible
@app.get("/api/docs", include_in_schema=True)
async def api_docs():
    """Redirect to FastAPI automatic documentation"""
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=True)
async def docs():
    """FastAPI automatic documentation"""
    return RedirectResponse(url="/redoc")

# Update app metadata
app.title = "DALI Legal AI - Enhanced Edition"
app.description = "Legal AI with Database Intelligence & Web Scraping"
app.version = "1.2.0"

# Add enhanced health check endpoint
@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint"""
    
    # Check Ollama connection
    try:
        import requests
        ollama_response = requests.get("http://127.0.0.1:11435/api/tags", timeout=5)
        ollama_status = ollama_response.status_code == 200
    except:
        ollama_status = False
    
    # Check MySQL database
    try:
        from src.core.database.manager import DatabaseManager
        from src.utils.config import load_config
        config = load_config('config/config.yaml')
        db_manager = DatabaseManager(config)
        mysql_status = db_manager.connect()
        if mysql_status:
            db_manager.close()
    except:
        mysql_status = False
    
    # Check sample database
    sample_db_exists = os.path.exists("data/sample_databases/legal_practice.db")
    
    # Check Firecrawl
    firecrawl_configured = bool(os.getenv('FIRECRAWL_API_KEY'))
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.2.0",
        "components": {
            "ollama": "online" if ollama_status else "offline",
            "mysql_database": "connected" if mysql_status else "disconnected",
            "sample_database": "available" if sample_db_exists else "missing",
            "firecrawl_api": "configured" if firecrawl_configured else "not_configured"
        },
        "features": {
            "database_intelligence": True,
            "web_scraping": True,
            "ai_analysis": True,
            "chart_generation": True,
            "natural_language_queries": True
        }
    }

@app.get("/api/system-info")
async def get_system_info():
    """Get comprehensive system information"""
    
    # Check available Ollama models
    try:
        import requests
        response = requests.get("http://127.0.0.1:11435/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model['name'] for model in response.json().get('models', [])]
        else:
            models = []
    except:
        models = []
    
    # Check database status
    try:
        from src.core.database.manager import DatabaseManager
        from src.utils.config import load_config
        config = load_config('config/config.yaml')
        db_manager = DatabaseManager(config)
        mysql_connected = db_manager.connect()
        if mysql_connected:
            tables = db_manager.get_tables()
            db_manager.close()
        else:
            tables = []
    except:
        mysql_connected = False
        tables = []
    
    # Check sample database
    sample_db_exists = os.path.exists("data/sample_databases/legal_practice.db")
    
    # Check Firecrawl
    firecrawl_configured = bool(os.getenv('FIRECRAWL_API_KEY'))
    
    # Check scraping services
    try:
        from src.core.scraping.scraping_manager import WebScrapingManager
        scraping_manager = WebScrapingManager(config)
        scraping_status = scraping_manager.get_scraping_status()
    except:
        scraping_status = {"firecrawl_available": False, "ollama_available": False}
    
    return {
        "system_name": "DALI Legal AI Enhanced",
        "version": "1.2.0",
        "description": "Legal AI with Database Intelligence & Web Scraping",
        "features": {
            "database_intelligence": True,
            "web_scraping": True,
            "ai_analysis": True,
            "chart_generation": True,
            "natural_language_queries": True,
            "legal_document_analysis": True,
            "batch_processing": True
        },
        "components": {
            "ollama_models": models,
            "mysql_database": {
                "connected": mysql_connected,
                "tables": len(tables) if mysql_connected else 0
            },
            "sample_database": sample_db_exists,
            "firecrawl_api": firecrawl_configured,
            "scraping_services": scraping_status
        },
        "api_endpoints": {
            "knowledge_base": "/api/knowledge-base",
            "web_scraping": "/api/web-scraping",
            "documentation": "/api/docs",
            "health_check": "/api/health",
            "system_info": "/api/system-info"
        },
        "sample_queries": {
            "knowledge_base": "Show me all clients with high value",
            "web_scraping": "Scrape SEC enforcement actions",
            "legal_analysis": "Analyze legal document relevance"
        }
    }

@app.get("/api/status")
async def get_status():
    """Quick status check for monitoring"""
    
    try:
        # Quick Ollama check
        import requests
        ollama_response = requests.get("http://127.0.0.1:11435/api/tags", timeout=2)
        ollama_ok = ollama_response.status_code == 200
    except:
        ollama_ok = False
    
    try:
        # Quick database check
        from src.core.database.manager import DatabaseManager
        from src.utils.config import load_config
        config = load_config('config/config.yaml')
        db_manager = DatabaseManager(config)
        db_ok = db_manager.connect()
        if db_ok:
            db_manager.close()
    except:
        db_ok = False
    
    return {
        "status": "healthy" if (ollama_ok and db_ok) else "degraded",
        "ollama": "online" if ollama_ok else "offline",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

# Main Index Route
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main index page - choose dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "DALI Legal AI - Choose Your Dashboard"
    })

# Unified Dashboard Routes - Clean and Simple
@app.get("/unified-user-dashboard", response_class=HTMLResponse)
async def unified_user_dashboard(request: Request):
    """Unified user dashboard with all features integrated"""
    return templates.TemplateResponse("unified_user_dashboard.html", {
        "request": request,
        "title": "DALI Legal AI - User Dashboard"
    })

@app.get("/unified-admin-dashboard", response_class=HTMLResponse)
async def unified_admin_dashboard(request: Request):
    """Unified admin dashboard with all administrative features"""
    return templates.TemplateResponse("unified_admin_dashboard.html", {
        "request": request,
        "title": "DALI Legal AI - Admin Dashboard"
    })

# Redirect old dashboard routes to unified versions
@app.get("/user-friendly-dashboard", response_class=HTMLResponse)
async def redirect_user_dashboard(request: Request):
    """Redirect to unified user dashboard"""
    return RedirectResponse(url="/unified-user-dashboard")

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def redirect_admin_dashboard(request: Request):
    """Redirect to unified admin dashboard"""
    return RedirectResponse(url="/unified-admin-dashboard")

@app.get("/enhanced-dashboard", response_class=HTMLResponse)
async def redirect_enhanced_dashboard(request: Request):
    """Redirect to unified user dashboard"""
    return RedirectResponse(url="/unified-user-dashboard")

@app.get("/enhanced-knowledge-base", response_class=HTMLResponse)
async def redirect_enhanced_kb(request: Request):
    """Redirect to unified user dashboard"""
    return RedirectResponse(url="/unified-user-dashboard")

# Authentication API Endpoints
@app.post("/api/login")
async def api_login(login_data: LoginRequest):
    """API endpoint for user login"""
    try:
        # Import user store from existing app
        from src.web.app import user_store, pwd_context
        
        # Get user from database
        user = user_store.get_user_by_username(login_data.username)
        if not user or not pwd_context.verify(login_data.password, user['password_hash']):
            return {"success": False, "message": "Invalid username or password"}
        
        # Check if user is active
        if not user.get('is_active', True):
            return {"success": False, "message": "Account is deactivated"}
        
        # Create user session data
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "email": user.get("email", ""),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", "")
        }
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_data
        }
        
    except Exception as e:
        return {"success": False, "message": f"Login failed: {str(e)}"}

@app.post("/api/signup")
async def api_signup(signup_data: SignupRequest):
    """API endpoint for user signup"""
    try:
        # Import user store from existing app
        from src.web.app import user_store, pwd_context
        
        # Check if username already exists
        if user_store.get_user_by_username(signup_data.username):
            return {"success": False, "message": "Username already exists"}
        
        # Check if email already exists
        cursor = user_store.conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (signup_data.email,))
        if cursor.fetchone():
            cursor.close()
            return {"success": False, "message": "Email already exists"}
        cursor.close()
        
        # Hash password
        password_hash = pwd_context.hash(signup_data.password)
        
        # Insert new user
        cursor = user_store.conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, 
                             company_name, job_title, phone, department, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (signup_data.username, signup_data.email, password_hash, 
              signup_data.first_name, signup_data.last_name, 
              signup_data.company_name, signup_data.job_title, 
              signup_data.phone, signup_data.department, signup_data.role, True))
        user_store.conn.commit()
        cursor.close()
        
        return {
            "success": True,
            "message": "Account created successfully"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Signup failed: {str(e)}"}

@app.post("/api/logout")
async def api_logout():
    """API endpoint for user logout"""
    return {"success": True, "message": "Logged out successfully"}

# Login and Signup Pages
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Modern login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login - DALI Legal AI"
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Modern signup page"""
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "title": "Sign Up - DALI Legal AI"
    })

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/sample_databases", exist_ok=True)
    os.makedirs("data/scraped_content", exist_ok=True)
    os.makedirs("static/charts", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("🚀 Starting DALI Legal AI - Enhanced Edition...")
    print("📊 Features: Database Intelligence, Web Scraping, AI Analysis")
    print("🌐 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔍 Knowledge Base API: http://localhost:8000/api/knowledge-base")
    print("🌐 Web Scraping API: http://localhost:8000/api/web-scraping")
    print("💚 Health Check: http://localhost:8000/api/health")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
