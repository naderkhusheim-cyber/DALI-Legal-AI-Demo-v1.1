#!/usr/bin/env python3
"""
Complete Database Workflow Example
Demonstrates Database Manager, SQL Generator, and Chart Generator working together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import DatabaseManager, SQLGenerator, ChartGenerator
from src.utils.config import load_config
import pandas as pd

def complete_workflow_example():
    """Demonstrate complete database workflow"""
    print("🚀 Complete Database Workflow Example\n")
    
    # Load project configuration
    config = load_config('config/config.yaml')
    
    # Initialize all components
    db_manager = DatabaseManager(config)
    sql_generator = SQLGenerator(config)
    chart_generator = ChartGenerator(config)
    
    print("📊 Database Connection Test:")
    if not db_manager.connect():
        print("❌ Failed to connect to database")
        return
    
    print("✅ Database connected successfully")
    
    print("\n🤖 AI Components Test:")
    if sql_generator.test_connection():
        print("✅ SQL Generator ready")
    else:
        print("❌ SQL Generator not available")
    
    if chart_generator.test_connection():
        print("✅ Chart Generator ready")
    else:
        print("❌ Chart Generator not available")
    
    # Get database schema
    schema_context = db_manager.get_schema_context()
    print(f"\n📋 Database schema loaded: {len(schema_context)} characters")
    
    # Example 1: Natural Language to SQL to Chart
    print("\n" + "="*60)
    print("1️⃣ NATURAL LANGUAGE TO SQL TO CHART WORKFLOW")
    print("="*60)
    
    natural_queries = [
        "Show me the top 5 attorneys by case count",
        "What is the revenue by client?",
        "Show me the distribution of case types"
    ]
    
    for i, query in enumerate(natural_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        
        # Step 1: Generate SQL
        print("   📝 Generating SQL...")
        sql_result = sql_generator.generate_sql(query, schema_context)
        
        if sql_result['success']:
            sql_query = sql_result['sql_query']
            print(f"   ✅ SQL: {sql_query}")
            
            # Step 2: Execute SQL
            print("   🔍 Executing query...")
            success, data = db_manager.execute_query(sql_query)
            
            if success and not data.empty:
                print(f"   ✅ Query executed - {len(data)} rows returned")
                print(f"   📊 Columns: {list(data.columns)}")
                
                # Step 3: Generate Chart
                print("   📈 Generating chart...")
                chart_result = chart_generator.generate_chart(data, query)
                
                if chart_result['success']:
                    print(f"   ✅ Chart generated: {chart_result['chart_config']['chart_type']}")
                    print(f"   📊 Title: {chart_result['chart_config']['title']}")
                    print(f"   💭 Reasoning: {chart_result['reasoning']}")
                else:
                    print(f"   ❌ Chart generation failed: {chart_result['error']}")
            else:
                print(f"   ❌ Query execution failed: {data if not success else 'No data returned'}")
        else:
            print(f"   ❌ SQL generation failed: {sql_result['error']}")
    
    # Example 2: Direct Analytics Queries
    print("\n" + "="*60)
    print("2️⃣ DIRECT ANALYTICS QUERIES")
    print("="*60)
    
    analytics_queries = [
        "SELECT practice_area, COUNT(*) as attorney_count FROM attorneys GROUP BY practice_area",
        "SELECT case_status, COUNT(*) as case_count FROM cases GROUP BY case_status",
        "SELECT client_id, COUNT(*) as case_count FROM cases GROUP BY client_id ORDER BY case_count DESC LIMIT 5"
    ]
    
    for i, query in enumerate(analytics_queries, 1):
        print(f"\n📊 Analytics Query {i}: {query}")
        
        success, data = db_manager.execute_query(query)
        
        if success and not data.empty:
            print(f"   ✅ Executed - {len(data)} rows")
            
            # Generate chart for this data
            chart_result = chart_generator.generate_chart(data, f"Analytics Query {i}")
            
            if chart_result['success']:
                print(f"   📈 Chart: {chart_result['chart_config']['chart_type']} - {chart_result['chart_config']['title']}")
            else:
                print(f"   ❌ Chart failed: {chart_result['error']}")
        else:
            print(f"   ❌ Query failed: {data if not success else 'No data'}")
    
    # Example 3: Database Statistics
    print("\n" + "="*60)
    print("3️⃣ DATABASE STATISTICS")
    print("="*60)
    
    stats = db_manager.get_table_stats()
    print("📊 Table Statistics:")
    for table, stat in stats.items():
        if 'error' not in stat:
            print(f"   {table}: {stat['row_count']} rows, {stat['column_count']} columns")
    
    # Example 4: Sample Data Visualization
    print("\n" + "="*60)
    print("4️⃣ SAMPLE DATA VISUALIZATION")
    print("="*60)
    
    # Get sample data from different tables
    sample_tables = ['clients', 'attorneys', 'cases']
    
    for table in sample_tables:
        print(f"\n📋 Sample data from {table}:")
        success, sample_data = db_manager.get_sample_data(table, 5)
        
        if success and not sample_data.empty:
            print(f"   ✅ Retrieved {len(sample_data)} rows")
            
            # Generate chart for sample data
            chart_result = chart_generator.generate_chart(sample_data, f"Sample data from {table}")
            
            if chart_result['success']:
                print(f"   📈 Chart: {chart_result['chart_config']['chart_type']}")
                print(f"   📊 Title: {chart_result['chart_config']['title']}")
            else:
                print(f"   ❌ Chart failed: {chart_result['error']}")
        else:
            print(f"   ❌ No data available")
    
    print("\n" + "="*60)
    print("✅ COMPLETE WORKFLOW TEST COMPLETED")
    print("="*60)
    
    # Close database connection
    db_manager.close()

if __name__ == "__main__":
    complete_workflow_example()
