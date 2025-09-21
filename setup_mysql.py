#!/usr/bin/env python3
"""
DALI Legal AI - MySQL Setup Script
Creates MySQL database and user for DALI system
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_mysql_database():
    """Create MySQL database and user for DALI"""
    
    # Database configuration
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',  # Using root for initial setup
        'password': 'NewPassword123!',  # Updated password
    }
    
    try:
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Create database
        print("Creating database 'dali_legal_ai'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS dali_legal_ai")
        
        # Create user
        print("Creating user 'dali_user'...")
        cursor.execute("CREATE USER IF NOT EXISTS 'dali_user'@'localhost' IDENTIFIED BY 'dali_password'")
        
        # Grant privileges
        print("Granting privileges...")
        cursor.execute("GRANT ALL PRIVILEGES ON dali_legal_ai.* TO 'dali_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        # Create tables
        print("Creating tables...")
        cursor.execute("USE dali_legal_ai")
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                company_name VARCHAR(100),
                job_title VARCHAR(100),
                employee_id VARCHAR(50),
                phone VARCHAR(20),
                department VARCHAR(50),
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings TEXT
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                document_type VARCHAR(50),
                source VARCHAR(255),
                content LONGTEXT NOT NULL,
                embedding LONGBLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_chats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender_id INT NOT NULL,
                receiver_id INT NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
        ''')
        
        # Activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Shared documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                shared_by_user_id INT NOT NULL,
                shared_with_user_id INT NOT NULL,
                shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id),
                FOREIGN KEY (shared_by_user_id) REFERENCES users (id),
                FOREIGN KEY (shared_with_user_id) REFERENCES users (id)
            )
        ''')
        
        # Document permission requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_permission_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                requester_id INT NOT NULL,
                uploader_id INT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id),
                FOREIGN KEY (requester_id) REFERENCES users (id),
                FOREIGN KEY (uploader_id) REFERENCES users (id)
            )
        ''')
        
        # Create admin user
        print("Creating admin user...")
        cursor.execute('''
            INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, role)
            VALUES ('admin', 'admin@dali.com', 'admin123', 'Admin', 'User', 'admin')
        ''')
        
        connection.commit()
        print("✅ MySQL database setup completed successfully!")
        print("Database: dali_legal_ai")
        print("User: dali_user")
        print("Password: dali_password")
        print("Admin user: admin / admin123")
        
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL service is running")
        print("2. Check if root password is required")
        print("3. Verify MySQL is installed correctly")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    print("DALI Legal AI - MySQL Setup")
    print("=" * 40)
    create_mysql_database()
