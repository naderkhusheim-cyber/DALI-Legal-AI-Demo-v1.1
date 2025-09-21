#!/usr/bin/env python3
"""
Example usage of the SQL Generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database.sql_generator import SQLGenerator
from src.core.database.manager import DatabaseManager
from src.utils.config import load_config

def example_sql_generation():
    """Demonstrate SQL generator usage"""
    print("📚 SQL Generator Usage Examples\n")
    
    # Load project configuration
    config = load_config('config/config.yaml')
    
    # Get database schema
    with DatabaseManager(config) as db:
        schema_context = db.get_schema_context()
        print("📋 Database schema loaded")
    
    # Create SQL generator
    generator = SQLGenerator(config)
    
    # Example 1: Basic client query
    print("\n1️⃣ Basic Client Query:")
    result = generator.generate_sql("Show me all clients", schema_context)
    if result['success']:
        print(f"   Query: {result['sql_query']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Example 2: Complex analytics query
    print("\n2️⃣ Complex Analytics Query:")
    result = generator.generate_sql("Show client revenue summary with case counts", schema_context)
    if result['success']:
        print(f"   Query: {result['sql_query']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Example 3: Attorney performance query
    print("\n3️⃣ Attorney Performance Query:")
    result = generator.generate_sql("List attorneys by practice area with case counts", schema_context)
    if result['success']:
        print(f"   Query: {result['sql_query']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Example 4: Date-based query
    print("\n4️⃣ Date-based Query:")
    result = generator.generate_sql("Find cases filed in the last 6 months", schema_context)
    if result['success']:
        print(f"   Query: {result['sql_query']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Example 5: Validation example
    print("\n5️⃣ SQL Validation:")
    test_sql = "SELECT * FROM clients WHERE status = 'Active'"
    validation = generator.validate_sql(test_sql)
    print(f"   Valid: {validation['valid']}")
    if validation['warnings']:
        print(f"   Warnings: {validation['warnings']}")
    if validation['errors']:
        print(f"   Errors: {validation['errors']}")
    
    print("\n✅ All examples completed successfully!")

if __name__ == "__main__":
    example_sql_generation()
