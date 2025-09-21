#!/usr/bin/env python3
"""
Web Scraping API Usage Examples
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_web_scraping_api():
    """Test the Web Scraping API endpoints"""
    print("🌐 Testing Web Scraping API...\n")
    
    # Base URL for the API
    base_url = "http://localhost:8000/api/web-scraping"
    
    # Test 1: Scraping Status
    print("1️⃣ Scraping Services Status:")
    try:
        response = requests.get(f"{base_url}/scraping-status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Firecrawl: {status['status']['firecrawl_available']}")
            print(f"   ✅ Ollama: {status['status']['ollama_available']}")
            print(f"   🔑 API Key: {status['status']['firecrawl_api_key_configured']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️ API server not running. Start with: python main.py")
        return
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return
    
    # Test 2: Test Firecrawl Connection
    print("\n2️⃣ Firecrawl Connection Test:")
    try:
        response = requests.get(f"{base_url}/test-firecrawl")
        if response.status_code == 200:
            result = response.json()
            print(f"   📡 Available: {result['firecrawl_available']}")
            print(f"   🔑 API Key: {result['api_key_configured']}")
            print(f"   🌐 Base URL: {result['base_url']}")
        else:
            print(f"   ❌ Firecrawl test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Firecrawl test error: {e}")
    
    # Test 3: Test Ollama Connection
    print("\n3️⃣ Ollama Connection Test:")
    try:
        response = requests.get(f"{base_url}/test-ollama")
        if response.status_code == 200:
            result = response.json()
            print(f"   🤖 Available: {result['ollama_available']}")
            print(f"   🌐 Base URL: {result['base_url']}")
            print(f"   📊 Model: {result['analysis_model']}")
        else:
            print(f"   ❌ Ollama test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ollama test error: {e}")
    
    # Test 4: Get Legal Targets
    print("\n4️⃣ Legal Targets:")
    try:
        response = requests.get(f"{base_url}/legal-targets")
        if response.status_code == 200:
            targets = response.json()
            print(f"   ✅ Found {targets['total_targets']} legal targets")
            print(f"   📊 Categories: {targets['total_categories']}")
            
            for category, sites in targets['legal_targets'].items():
                print(f"      {category}: {len(sites)} sites")
        else:
            print(f"   ❌ Legal targets failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Legal targets error: {e}")
    
    # Test 5: Get Sample Queries
    print("\n5️⃣ Sample Scraping Queries:")
    try:
        response = requests.get(f"{base_url}/sample-scraping-queries")
        if response.status_code == 200:
            queries = response.json()
            print(f"   ✅ Found {queries['total_queries']} sample queries")
            
            for i, query in enumerate(queries['sample_queries'][:2], 1):
                print(f"      {i}. {query['query']}")
                print(f"         URL: {query['url']}")
                print(f"         Method: {query['method']}")
        else:
            print(f"   ❌ Sample queries failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sample queries error: {e}")
    
    # Test 6: Basic Website Scraping
    print("\n6️⃣ Basic Website Scraping:")
    try:
        scrape_data = {
            "url": "https://example.com",
            "method": "beautifulsoup",
            "options": {"timeout": 10}
        }
        
        response = requests.post(f"{base_url}/scrape", json=scrape_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Scraping successful")
            print(f"   🌐 URL: {result['url']}")
            print(f"   🔧 Method: {result['method']}")
            print(f"   📄 Content length: {result['content_length']} characters")
            print(f"   🔗 Links found: {len(result.get('links', []))}")
            
            if 'analysis' in result and result['analysis']:
                analysis = result['analysis']
                print(f"   📊 Content type: {analysis.get('content_type', 'Unknown')}")
                print(f"   ⚖️ Legal relevance: {analysis.get('legal_relevance', 'Unknown')}")
        else:
            print(f"   ❌ Scraping failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Scraping error: {e}")
    
    # Test 7: Document Search
    print("\n7️⃣ Document Search:")
    try:
        doc_search_data = {
            "url": "https://example.com",
            "doc_types": ["pdf", "doc", "docx", "txt"]
        }
        
        response = requests.post(f"{base_url}/find-documents", json=doc_search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Document search completed")
            print(f"   🌐 URL: {result['url']}")
            print(f"   📄 Documents found: {result['documents_found']}")
            
            if result['documents']:
                for doc in result['documents'][:3]:  # Show first 3
                    print(f"      - {doc['filename']} ({doc['type']})")
        else:
            print(f"   ❌ Document search failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Document search error: {e}")
    
    # Test 8: Batch Scraping
    print("\n8️⃣ Batch Scraping:")
    try:
        batch_data = {
            "urls": [
                "https://example.com",
                "https://httpbin.org/html",
                "https://httpbin.org/json"
            ],
            "method": "beautifulsoup"
        }
        
        response = requests.post(f"{base_url}/batch-scrape", json=batch_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Batch scraping completed")
            print(f"   📊 Total URLs: {result['total_urls']}")
            print(f"   ✅ Successful: {result['successful_scrapes']}")
            print(f"   ❌ Failed: {result['failed_scrapes']}")
            
            for scrape in result['results'][:2]:  # Show first 2 results
                print(f"      - {scrape['url']}: {scrape['content_length']} chars")
        else:
            print(f"   ❌ Batch scraping failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Batch scraping error: {e}")
    
    # Test 9: Legal Analysis
    print("\n9️⃣ Legal Analysis:")
    try:
        analysis_data = {
            "url": "https://example.com",
            "analysis_type": "legal_relevance"
        }
        
        response = requests.post(f"{base_url}/legal-analysis", json=analysis_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Legal analysis completed")
            print(f"   🌐 URL: {result['url']}")
            print(f"   📊 Analysis type: {result['analysis_type']}")
            print(f"   📄 Content length: {result['content_length']}")
            
            analysis = result['enhanced_analysis']
            print(f"   📈 Relevance score: {analysis.get('relevance_score', 'N/A')}")
            print(f"   🏷️ Key concepts: {', '.join(analysis.get('key_legal_concepts', [])[:3])}")
        else:
            print(f"   ❌ Legal analysis failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Legal analysis error: {e}")
    
    # Test 10: Case Analysis
    print("\n🔟 Case Analysis:")
    try:
        case_analysis_data = {
            "url": "https://example.com",
            "analysis_type": "case_analysis"
        }
        
        response = requests.post(f"{base_url}/legal-analysis", json=case_analysis_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Case analysis completed")
            
            analysis = result['enhanced_analysis']
            print(f"   📊 Case indicators: {', '.join(analysis.get('case_indicators', [])[:3])}")
            print(f"   🏢 Legal entities: {', '.join(analysis.get('legal_entities', [])[:3])}")
            print(f"   📋 Case status: {analysis.get('case_status', 'Unknown')}")
            print(f"   ⚖️ Jurisdiction: {analysis.get('jurisdiction', 'Unknown')}")
        else:
            print(f"   ❌ Case analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Case analysis error: {e}")
    
    print("\n✅ Web Scraping API testing completed!")

if __name__ == "__main__":
    test_web_scraping_api()
