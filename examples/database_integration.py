#!/usr/bin/env python3
"""
Comprehensive example of Database Manager and SQL Generator integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager, SQLGenerator
from src.utils.config import load_config

def comprehensive_example():
    """Demonstrate comprehensive database and SQL generation integration"""
    print("🚀 Comprehensive Database Integration Example\n")
    
    # Load project configuration
    config = load_config('config/config.yaml')
    
    # Initialize components
    db_manager = DatabaseManager(config)
    sql_generator = SQLGenerator(config)
    
    print("📊 Database Connection Test:")
    if db_manager.connect():
        print("✅ Database connected successfully")
        
        # Get database information
        info = db_manager.get_connection_info()
        print(f"   Database: {info['database']}")
        print(f"   Tables: {info['table_count']}")
        print(f"   Host: {info['host']}")
        
        # Get schema for SQL generation
        schema_context = db_manager.get_schema_context()
        print(f"   Schema loaded: {len(schema_context)} characters")
        
    else:
        print("❌ Failed to connect to database")
        return
    
    print("\n🤖 SQL Generator Test:")
    if sql_generator.test_connection():
        print("✅ Ollama connection successful")
        print(f"   Model: {sql_generator.model}")
        print(f"   URL: {sql_generator.base_url}")
    else:
        print("❌ Failed to connect to Ollama")
        return
    
    print("\n🔍 Natural Language to SQL Examples:")
    
    # Example queries
    queries = [
        "Show me all active clients",
        "Find the top 5 attorneys by case count",
        "What is the total revenue by client?",
        "Show cases filed in the last 30 days",
        "List all billable hours for this month"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}️⃣ Query: '{query}'")
        
        # Generate SQL
        result = sql_generator.generate_sql(query, schema_context)
        
        if result['success']:
            sql_query = result['sql_query']
            print(f"   Generated SQL: {sql_query}")
            
            # Validate SQL
            validation = sql_generator.validate_sql(sql_query)
            if validation['warnings']:
                print(f"   ⚠️  Warnings: {validation['warnings']}")
            
            # Try to execute the query (if it's safe)
            if not any(keyword in sql_query.upper() for keyword in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']):
                try:
                    success, data = db_manager.execute_query(sql_query)
                    if success:
                        print(f"   ✅ Query executed successfully - {len(data)} rows returned")
                        if len(data) > 0:
                            print(f"   📋 Sample data: {list(data.columns)}")
                    else:
                        print(f"   ❌ Query execution failed: {data}")
                except Exception as e:
                    print(f"   ⚠️  Query execution error: {e}")
            else:
                print("   ⚠️  Skipping execution - query contains potentially dangerous operations")
        else:
            print(f"   ❌ SQL generation failed: {result['error']}")
    
    print("\n📈 Database Analytics:")
    
    # Get table statistics
    stats = db_manager.get_table_stats()
    print("   Table Statistics:")
    for table, stat in stats.items():
        if 'error' not in stat:
            print(f"   - {table}: {stat['row_count']} rows, {stat['column_count']} columns")
    
    # Test complex analytics
    print("\n   Complex Analytics Queries:")
    analytics_queries = [
        "SELECT COUNT(*) as total_clients FROM clients",
        "SELECT practice_area, COUNT(*) as attorney_count FROM attorneys GROUP BY practice_area",
        "SELECT case_status, COUNT(*) as case_count FROM cases GROUP BY case_status"
    ]
    
    for query in analytics_queries:
        success, result = db_manager.execute_query(query)
        if success and not result.empty:
            print(f"   ✅ {query}: {result.iloc[0].to_dict()}")
        else:
            print(f"   ❌ {query}: Failed")
    
    print("\n✅ Comprehensive integration test completed!")
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    comprehensive_example()
