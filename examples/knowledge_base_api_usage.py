#!/usr/bin/env python3
"""
Knowledge Base API Usage Examples
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_knowledge_base_api():
    """Test the Knowledge Base API endpoints"""
    print("🧪 Testing Knowledge Base API...\n")
    
    # Base URL for the API
    base_url = "http://localhost:8000/api/knowledge-base"
    
    # Test 1: Health Check
    print("1️⃣ Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Status: {health['status']}")
            print(f"   📊 Database: {health['database']}")
            print(f"   🤖 Ollama: {health['ollama']}")
            print(f"   📈 Chart Generator: {health['chart_generator']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️ API server not running. Start with: python main.py")
        return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Connection Status
    print("\n2️⃣ Connection Status:")
    try:
        response = requests.get(f"{base_url}/connection-status")
        if response.status_code == 200:
            status = response.json()
            print(f"   📊 Database Connected: {status['connected']}")
            print(f"   🤖 Ollama Available: {status['ollama_available']}")
            print(f"   📈 Chart Generator Available: {status['chart_generator_available']}")
            if status['connection_info']:
                print(f"   🔗 Database Type: {status['database_type']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test 3: Connect to Database
    print("\n3️⃣ Database Connection:")
    try:
        connection_data = {
            "db_type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "dali_legal_ai",
            "username": "dali_user",
            "password": "dali_password"
        }
        
        response = requests.post(f"{base_url}/connect", json=connection_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Connection failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 4: Get Database Schema
    print("\n4️⃣ Database Schema:")
    try:
        response = requests.get(f"{base_url}/schema")
        if response.status_code == 200:
            schema = response.json()
            print(f"   ✅ Schema retrieved successfully")
            print(f"   📊 Tables: {len(schema['schema'])} tables found")
            for table_name in list(schema['schema'].keys())[:5]:  # Show first 5 tables
                print(f"      - {table_name}")
        else:
            print(f"   ❌ Schema retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Schema error: {e}")
    
    # Test 5: Get Tables
    print("\n5️⃣ Available Tables:")
    try:
        response = requests.get(f"{base_url}/tables")
        if response.status_code == 200:
            tables = response.json()
            print(f"   ✅ Found {tables['table_count']} tables")
            for table in tables['tables'][:5]:  # Show first 5 tables
                print(f"      - {table}")
        else:
            print(f"   ❌ Table listing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Table listing error: {e}")
    
    # Test 6: Sample Queries
    print("\n6️⃣ Sample Queries:")
    try:
        response = requests.get(f"{base_url}/sample-queries")
        if response.status_code == 200:
            queries = response.json()
            print(f"   ✅ Found {queries['total_queries']} sample queries")
            for query in queries['sample_queries'][:3]:  # Show first 3
                print(f"      - {query['question']} ({query['category']})")
        else:
            print(f"   ❌ Sample queries failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sample queries error: {e}")
    
    # Test 7: Natural Language Query
    print("\n7️⃣ Natural Language Query:")
    try:
        query_data = {
            "natural_language": "Show me all clients"
        }
        
        response = requests.post(f"{base_url}/generate-sql", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SQL Generated: {result['sql_query']}")
            print(f"   🤖 Model Used: {result['model_used']}")
        else:
            print(f"   ❌ SQL generation failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ SQL generation error: {e}")
    
    # Test 8: Execute Query
    print("\n8️⃣ Execute Query:")
    try:
        query_data = {
            "query": "SELECT * FROM clients LIMIT 5",
            "natural_language": "Show me sample clients"
        }
        
        response = requests.post(f"{base_url}/execute-query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query executed successfully")
            print(f"   📊 Rows returned: {result['row_count']}")
            print(f"   📋 Columns: {', '.join(result['columns'][:3])}...")  # Show first 3 columns
        else:
            print(f"   ❌ Query execution failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Query execution error: {e}")
    
    # Test 9: Generate Chart
    print("\n9️⃣ Generate Chart:")
    try:
        query_data = {
            "query": "SELECT practice_area, COUNT(*) as attorney_count FROM attorneys GROUP BY practice_area",
            "natural_language": "Show attorney count by practice area"
        }
        
        response = requests.post(f"{base_url}/generate-chart", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chart generated successfully")
            print(f"   📊 Chart type: {result['chart_config']['chart_type']}")
            print(f"   📈 Data points: {result['data_points']}")
            print(f"   💭 Reasoning: {result['reasoning'][:100]}...")
        else:
            print(f"   ❌ Chart generation failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Chart generation error: {e}")
    
    # Test 10: Complete Natural Language Pipeline
    print("\n🔟 Complete Natural Language Pipeline:")
    try:
        query_data = {
            "natural_language": "Show me the top 3 attorneys by case count"
        }
        
        response = requests.post(f"{base_url}/natural-language-query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Complete pipeline executed successfully")
            print(f"   📝 Natural Language: {result['natural_language']}")
            print(f"   🔍 SQL Generated: {result['sql_query']}")
            print(f"   📊 Rows returned: {result['row_count']}")
            print(f"   📈 Chart type: {result['chart_config']['chart_type']}")
            print(f"   🤖 Model used: {result['model_used']}")
        else:
            print(f"   ❌ Pipeline failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Pipeline error: {e}")
    
    print("\n✅ Knowledge Base API testing completed!")

if __name__ == "__main__":
    test_knowledge_base_api()
