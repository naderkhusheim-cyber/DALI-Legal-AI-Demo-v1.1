#!/usr/bin/env python3
"""
Example usage of the Database Manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database.manager import DatabaseManager

def example_usage():
    """Demonstrate database manager usage"""
    print("📚 Database Manager Usage Examples\n")
    
    # Example 1: Basic connection and query
    print("1️⃣ Basic Connection and Query:")
    with DatabaseManager() as db:
        if db.is_connected():
            success, result = db.execute_query("SELECT COUNT(*) as total FROM clients")
            if success:
                print(f"   Total clients: {result.iloc[0]['total']}")
        else:
            print("   ❌ Failed to connect to database")
    
    # Example 2: Get table information
    print("\n2️⃣ Table Information:")
    with DatabaseManager() as db:
        clients_info = db.get_table_info('clients')
        if clients_info:
            print(f"   Table: {clients_info['name']}")
            print(f"   Columns: {clients_info['column_count']}")
            print(f"   Primary Keys: {clients_info['primary_keys']}")
    
    # Example 3: Sample data retrieval
    print("\n3️⃣ Sample Data Retrieval:")
    with DatabaseManager() as db:
        success, sample = db.get_sample_data('attorneys', 3)
        if success:
            print(f"   Retrieved {len(sample)} attorney records:")
            for _, row in sample.iterrows():
                print(f"   - {row['name']} ({row['practice_area']})")
    
    # Example 4: Complex analytics query
    print("\n4️⃣ Complex Analytics Query:")
    with DatabaseManager() as db:
        success, result = db.execute_query("""
            SELECT 
                a.name as attorney_name,
                a.practice_area,
                COUNT(cs.case_id) as total_cases,
                AVG(cs.case_value) as avg_case_value,
                SUM(bh.total_amount) as total_billed
            FROM attorneys a
            LEFT JOIN cases cs ON a.attorney_id = cs.attorney_id
            LEFT JOIN billable_hours bh ON a.attorney_id = bh.attorney_id
            GROUP BY a.attorney_id
            ORDER BY total_billed DESC
        """)
        
        if success:
            print("   Attorney Performance Summary:")
            for _, row in result.iterrows():
                print(f"   - {row['attorney_name']}: {row['total_cases']} cases, "
                      f"${row['avg_case_value']:,.0f} avg value, ${row['total_billed']:,.2f} billed")
    
    # Example 5: Schema context for AI
    print("\n5️⃣ Schema Context for AI:")
    with DatabaseManager() as db:
        schema_context = db.get_schema_context()
        print(f"   Schema context: {len(schema_context)} characters")
        print("   First 200 characters:")
        print(f"   {schema_context[:200]}...")
    
    print("\n✅ All examples completed successfully!")

if __name__ == "__main__":
    example_usage()
