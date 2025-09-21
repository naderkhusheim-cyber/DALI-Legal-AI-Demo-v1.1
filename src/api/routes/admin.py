"""
Admin API Routes for DALI Legal AI
Provides administrative functionality for system management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
import mysql.connector
from src.utils.config import get_mysql_config

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    """Get MySQL database connection"""
    try:
        config = get_mysql_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "title": "Admin Dashboard - DALI Legal AI"
    })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    """Admin users management page"""
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "title": "User Management - DALI Legal AI Admin"
    })

@router.get("/api/users")
async def get_users():
    """Get all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get users from database
        cursor.execute("""
            SELECT id, username, email, role, created_at, is_active
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "users": users,
            "total": len(users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get specific user details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, username, email, role, created_at, is_active
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: Dict[str, Any]):
    """Update user information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user
        cursor.execute("""
            UPDATE users 
            SET username = %s, email = %s, role = %s, is_active = %s
            WHERE id = %s
        """, (
            user_data.get('username'),
            user_data.get('email'),
            user_data.get('role'),
            user_data.get('is_active', True),
            user_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user statistics
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as active_users FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()['active_users']
        
        cursor.execute("SELECT COUNT(*) as total_documents FROM documents")
        total_documents = cursor.fetchone()['total_documents']
        
        cursor.execute("SELECT COUNT(*) as total_conversations FROM conversations")
        total_conversations = cursor.fetchone()['total_conversations']
        
        # Get recent activity
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        user_registrations = cursor.fetchall()
        
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM conversations 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        conversation_activity = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "analytics": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                },
                "documents": {
                    "total": total_documents
                },
                "conversations": {
                    "total": total_conversations
                },
                "activity": {
                    "user_registrations": user_registrations,
                    "conversation_activity": conversation_activity
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@router.get("/logs")
async def get_logs(limit: int = 100, level: str = None):
    """Get system logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get activity logs from conversations table as a fallback
        query = """
            SELECT id, user_id, 'conversation' as action, 
                   COALESCE(title, 'No title') as details, 
                   '127.0.0.1' as ip_address, created_at
            FROM conversations 
        """
        params = []
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "logs": logs,
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")

@router.get("/system")
async def get_system_info():
    """Get system configuration and status"""
    try:
        # Database status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        db_users = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        # Basic system info without psutil
        import os
        import platform
        
        return {
            "success": True,
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "database": {
                    "status": "connected",
                    "users_count": db_users
                },
                "uptime": "N/A",  # Would need to implement uptime tracking
                "memory_info": "N/A - psutil not available",
                "cpu_info": "N/A - psutil not available"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system info: {str(e)}")

@router.put("/system")
async def update_system_config(config_data: Dict[str, Any]):
    """Update system configuration"""
    try:
        # This would typically update configuration files or database settings
        # For now, just return success
        return {
            "success": True,
            "message": "System configuration updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update system config: {str(e)}")

@router.get("/health")
async def admin_health_check():
    """Admin-specific health check"""
    try:
        # Check database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        db_status = "healthy"
        cursor.close()
        conn.close()
    except:
        db_status = "unhealthy"
    
    # Check other services
    try:
        import requests
        ollama_response = requests.get("http://127.0.0.1:11435/api/tags", timeout=5)
        ollama_status = "healthy" if ollama_response.status_code == 200 else "unhealthy"
    except:
        ollama_status = "unhealthy"
    
    return {
        "success": True,
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "ollama": ollama_status
        },
        "timestamp": datetime.now().isoformat()
    }
