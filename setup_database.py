#!/usr/bin/env python3
"""
DALI Legal AI - Database Setup Script
Creates SQLite database with all necessary tables
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Create SQLite database with all necessary tables"""
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "dali_users.db"
    
    # Remove existing database if it exists
    if db_path.exists():
        db_path.unlink()
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            company_name TEXT,
            job_title TEXT,
            employee_id TEXT,
            phone TEXT,
            department TEXT,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            last_active DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create documents table
    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            document_type TEXT,
            source TEXT,
            content TEXT,
            embedding BLOB,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            conversation_type TEXT DEFAULT 'legal_research',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create conversation_messages table
    cursor.execute('''
        CREATE TABLE conversation_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_type TEXT NOT NULL,
            message TEXT NOT NULL,
            metadata TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    ''')
    
    # Create user_chats table
    cursor.execute('''
        CREATE TABLE user_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create shared_documents table
    cursor.execute('''
        CREATE TABLE shared_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            shared_with_user_id INTEGER NOT NULL,
            shared_by_user_id INTEGER NOT NULL,
            shared_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (shared_by_user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create activity_log table
    cursor.execute('''
        CREATE TABLE activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT,
            event_data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Create document_permission_requests table
    cursor.execute('''
        CREATE TABLE document_permission_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            requester_id INTEGER NOT NULL,
            uploader_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create conversation_memory table
    cursor.execute('''
        CREATE TABLE conversation_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            message_type TEXT NOT NULL, -- 'user' or 'assistant'
            message_content TEXT NOT NULL,
            context_data TEXT, -- JSON string for storing additional context
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create conversation_sessions table
    cursor.execute('''
        CREATE TABLE conversation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT UNIQUE NOT NULL,
            session_name TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_conversation_memory_user_session ON conversation_memory(user_id, session_id)')
    cursor.execute('CREATE INDEX idx_conversation_memory_created_at ON conversation_memory(created_at)')
    cursor.execute('CREATE INDEX idx_conversation_sessions_user ON conversation_sessions(user_id)')
    
    # Create admin user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin_password_hash = pwd_context.hash("1234")
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ("admin1", "admin1@example.com", admin_password_hash, "admin", "Admin", "User"))
    
    # Create test user
    test_password_hash = pwd_context.hash("test123")
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ("testuser", "test@example.com", test_password_hash, "user", "Test", "User"))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully at: {db_path}")
    print("📋 Created tables:")
    print("  - users")
    print("  - documents") 
    print("  - conversations")
    print("  - conversation_messages")
    print("  - user_chats")
    print("  - shared_documents")
    print("  - activity_log")
    print("  - document_permission_requests")
    print("  - conversation_memory")
    print("  - conversation_sessions")
    print("\n👤 Created users:")
    print("  - admin1 / 1234 (admin)")
    print("  - testuser / test123 (user)")
    
    return db_path

if __name__ == "__main__":
    create_database()
