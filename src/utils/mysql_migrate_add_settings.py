import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mysql.connector
from utils.config import get_mysql_config

def add_settings_column():
    config = get_mysql_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    # Check if 'settings' column exists
    cursor.execute("SHOW COLUMNS FROM users LIKE 'settings';")
    result = cursor.fetchone()
    if result:
        print("Column 'settings' already exists. No migration needed.")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN settings TEXT;")
        conn.commit()
        print("Column 'settings' added to 'users' table.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    add_settings_column()
