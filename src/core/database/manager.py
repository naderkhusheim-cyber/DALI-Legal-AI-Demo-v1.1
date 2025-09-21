"""
Database Manager for DALI Legal AI Enhanced Features
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from typing import Dict, List, Optional, Any, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations for MySQL"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.connection = None
        self.engine = None
        self.db_type = "MySQL"
        self.schema = {}
        # Extract MySQL config from the full config
        if config and 'mysql' in config:
            self.config = config['mysql']
        else:
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default MySQL configuration"""
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'dali_user',
            'password': 'dali_password',
            'database': 'dali_legal_ai'
        }
    
    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            # Create MySQL connection
            self.connection = mysql.connector.connect(**self.config)
            
            # Create SQLAlchemy engine for pandas operations
            connection_string = f"mysql+pymysql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            self.engine = create_engine(connection_string)
            
            logger.info("Successfully connected to MySQL database")
            self.load_schema()
            return True
            
        except Error as e:
            logger.error(f"MySQL connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def load_schema(self):
        """Load database schema"""
        try:
            if not self.connection:
                return
                
            cursor = self.connection.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            self.schema = {}
            for table in tables:
                table_name = table[0]
                
                # Get column information
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                self.schema[table_name] = [
                    {
                        'name': col[0],
                        'type': col[1],
                        'nullable': col[2] == 'YES',
                        'key': col[3],
                        'default': col[4],
                        'extra': col[5]
                    }
                    for col in columns
                ]
            
            cursor.close()
            logger.info(f"Loaded schema for {len(self.schema)} tables")
            
        except Error as e:
            logger.error(f"Schema loading error: {e}")
        except Exception as e:
            logger.error(f"Schema loading error: {e}")
    
    def execute_query(self, sql_query: str) -> Tuple[bool, Any]:
        """Execute SQL query and return results"""
        try:
            if not self.engine:
                return False, "No database connection"
            
            df = pd.read_sql_query(sql_query, self.engine)
            return True, df
            
        except Error as e:
            logger.error(f"Query execution error: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return False, str(e)
    
    def execute_raw_query(self, sql_query: str, params: Tuple = None) -> Tuple[bool, Any]:
        """Execute raw SQL query using MySQL connector"""
        try:
            if not self.connection:
                return False, "No database connection"
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql_query, params)
            
            if sql_query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return True, results
            else:
                self.connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return True, affected_rows
                
        except Error as e:
            logger.error(f"Raw query execution error: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Raw query execution error: {e}")
            return False, str(e)
    
    def get_schema_context(self) -> str:
        """Get schema context for AI"""
        context = "MySQL Database Tables and Columns:\n\n"
        
        for table_name, columns in self.schema.items():
            context += f"Table: {table_name}\n"
            for col in columns:
                key_info = f" ({col['key']})" if col['key'] else ""
                nullable_info = " NULL" if col['nullable'] else " NOT NULL"
                context += f"  - {col['name']} ({col['type']}){key_info}{nullable_info}\n"
            context += "\n"
            
        return context
    
    def get_tables(self) -> List[str]:
        """Get list of all table names"""
        return list(self.schema.keys())
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific table"""
        if table_name not in self.schema:
            return None
        
        columns = self.schema[table_name]
        primary_keys = [col['name'] for col in columns if col['key'] == 'PRI']
        foreign_keys = [col['name'] for col in columns if col['key'] == 'MUL']
        
        return {
            'name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'column_count': len(columns)
        }
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> Tuple[bool, Any]:
        """Get sample data from a table"""
        if table_name not in self.schema:
            return False, f"Table '{table_name}' not found"
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get statistics about all tables"""
        stats = {}
        
        for table_name in self.schema.keys():
            try:
                # Get row count
                success, result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                if success and not result.empty:
                    row_count = result.iloc[0]['count']
                else:
                    row_count = 0
                
                stats[table_name] = {
                    'row_count': row_count,
                    'column_count': len(self.schema[table_name])
                }
            except Exception as e:
                stats[table_name] = {
                    'row_count': 0,
                    'column_count': len(self.schema[table_name]),
                    'error': str(e)
                }
        
        return stats
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if self.connection and self.connection.is_connected():
                return True
            return False
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            'connected': self.is_connected(),
            'db_type': self.db_type,
            'host': self.config.get('host', 'unknown'),
            'database': self.config.get('database', 'unknown'),
            'tables': list(self.schema.keys()) if self.schema else [],
            'table_count': len(self.schema),
            'user': self.config.get('user', 'unknown')
        }
    
    def close(self):
        """Close database connection"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Convenience function to create a database manager instance
def create_database_manager(config: Dict[str, Any] = None) -> DatabaseManager:
    """Create a new DatabaseManager instance"""
    return DatabaseManager(config)

# Test function
def test_database_manager():
    """Test the database manager functionality"""
    print("🧪 Testing Database Manager...")
    
    with DatabaseManager() as db:
        if db.is_connected():
            print("✅ Database connected successfully")
            
            # Test schema loading
            info = db.get_connection_info()
            print(f"📊 Found {info['table_count']} tables")
            
            # Test query execution
            success, result = db.execute_query("SELECT COUNT(*) as total FROM clients")
            if success:
                print(f"👥 Clients in database: {result.iloc[0]['total']}")
            
            # Test table stats
            stats = db.get_table_stats()
            print("📈 Table Statistics:")
            for table, stat in stats.items():
                print(f"  {table}: {stat['row_count']} rows, {stat['column_count']} columns")
            
            print("✅ Database Manager test completed successfully")
        else:
            print("❌ Failed to connect to database")

if __name__ == "__main__":
    test_database_manager()
