#!/usr/bin/env python3
"""
Web Scraping Manager Usage Examples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.scraping import WebScrapingManager
from src.utils.config import load_config

def scraping_manager_examples():
    """Demonstrate web scraping manager usage"""
    print("🌐 Web Scraping Manager Usage Examples\n")
    
    # Load project configuration
    config = load_config('config/config.yaml')
    manager = WebScrapingManager(config)
    
    # Show status
    print("📊 Scraping Services Status:")
    status = manager.get_scraping_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Example 1: Basic scraping
    print("\n1️⃣ Basic Web Scraping:")
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Scraping: {url}")
        result = manager.scrape_url(url, method='beautifulsoup')
        
        if result['success']:
            print(f"   ✅ Success - Method: {result['method']}")
            print(f"   📄 Content length: {len(result['content'])} characters")
            print(f"   🔗 Links found: {len(result.get('links', []))}")
            
            if 'analysis' in result and 'summary' in result['analysis']:
                print(f"   📝 Summary: {result['analysis']['summary'][:100]}...")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Example 2: Document finding
    print("\n2️⃣ Document Finding:")
    doc_url = "https://httpbin.org/html"  # Using a test URL
    print(f"🔍 Finding documents on: {doc_url}")
    
    doc_result = manager.find_documents(doc_url, ['pdf', 'doc', 'docx', 'txt'])
    
    if doc_result['success']:
        print(f"   ✅ Found {doc_result['documents_found']} documents")
        for doc in doc_result['documents'][:3]:  # Show first 3
            print(f"   📄 {doc['filename']} ({doc['type']})")
    else:
        print(f"   ❌ Document search failed: {doc_result['error']}")
    
    # Example 3: Firecrawl vs BeautifulSoup comparison
    print("\n3️⃣ Scraping Method Comparison:")
    test_url = "https://example.com"
    
    print(f"🔍 Testing both methods on: {test_url}")
    
    # Test BeautifulSoup
    bs_result = manager.scrape_url(test_url, method='beautifulsoup')
    print(f"\n📊 BeautifulSoup Results:")
    if bs_result['success']:
        print(f"   ✅ Success - Content: {len(bs_result['content'])} chars")
        print(f"   🔗 Links: {len(bs_result.get('links', []))}")
    else:
        print(f"   ❌ Failed: {bs_result['error']}")
    
    # Test Firecrawl (if available)
    if manager.test_firecrawl_connection():
        fc_result = manager.scrape_url(test_url, method='firecrawl')
        print(f"\n📊 Firecrawl Results:")
        if fc_result['success']:
            print(f"   ✅ Success - Content: {len(fc_result['content'])} chars")
            print(f"   📊 Metadata: {len(fc_result.get('metadata', {}))} fields")
        else:
            print(f"   ❌ Failed: {fc_result['error']}")
    else:
        print(f"\n📊 Firecrawl: Not available")
    
    # Example 4: Content analysis
    print("\n4️⃣ Content Analysis:")
    analysis_url = "https://example.com"
    print(f"🔍 Analyzing content from: {analysis_url}")
    
    result = manager.scrape_url(analysis_url)
    if result['success'] and 'analysis' in result:
        analysis = result['analysis']
        print(f"   📊 Content Type: {analysis.get('content_type', 'Unknown')}")
        print(f"   ⚖️ Legal Relevance: {analysis.get('legal_relevance', 'Unknown')}")
        print(f"   📝 Summary: {analysis.get('summary', 'No summary available')}")
        print(f"   📈 Credibility Score: {analysis.get('credibility_score', 'N/A')}")
        print(f"   📊 Word Count: {analysis.get('word_count', 'Unknown')}")
        
        if 'key_topics' in analysis:
            print(f"   🏷️ Key Topics: {', '.join(analysis['key_topics'][:3])}")
        
        if 'legal_entities' in analysis:
            print(f"   🏢 Legal Entities: {', '.join(analysis['legal_entities'][:3])}")
    else:
        print(f"   ❌ Analysis not available")
    
    # Example 5: Error handling
    print("\n5️⃣ Error Handling:")
    invalid_urls = [
        "https://invalid-url-that-does-not-exist.com",
        "https://httpbin.org/status/404",
        "not-a-url"
    ]
    
    for url in invalid_urls:
        print(f"🔍 Testing invalid URL: {url}")
        result = manager.scrape_url(url)
        if not result['success']:
            print(f"   ❌ Expected error: {result['error']}")
        else:
            print(f"   ⚠️ Unexpected success")
    
    print("\n✅ All scraping manager examples completed!")

if __name__ == "__main__":
    scraping_manager_examples()
