"""
Web Scraping Manager for DALI Legal AI
"""

import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import re
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebScrapingManager:
    """Manages web scraping operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Use project configuration or environment variables
        if config:
            firecrawl_config = config.get('firecrawl', {})
            ollama_config = config.get('ollama', {})
            
            self.firecrawl_api_key = firecrawl_config.get('api_key') or os.getenv('FIRECRAWL_API_KEY')
            self.firecrawl_base_url = "https://api.firecrawl.dev/v0"
            
            # Handle Ollama configuration
            host = ollama_config.get('host', 'localhost')
            if ':' in host:
                self.ollama_host = host.split(':')[0]
                self.ollama_port = int(host.split(':')[1])
            else:
                self.ollama_host = host
                self.ollama_port = ollama_config.get('port', 11435)
            
            self.analysis_model = ollama_config.get('model', 'llama3.2:1b')
        else:
            self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
            self.firecrawl_base_url = "https://api.firecrawl.dev/v0"
            self.ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            self.ollama_port = int(os.getenv('OLLAMA_PORT', '11435'))
            self.analysis_model = os.getenv('ANALYSIS_MODEL', 'llama3.2:1b')
        
        self.ollama_base_url = f"http://{self.ollama_host}:{self.ollama_port}"
    
    def scrape_with_firecrawl(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape website using Firecrawl API"""
        
        if not self.firecrawl_api_key:
            return {'success': False, 'error': 'Firecrawl API key not configured'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.firecrawl_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'formats': ['markdown', 'html'],
                'onlyMainContent': True,
                'waitFor': options.get('wait_time', 2000) if options else 2000
            }
            
            response = requests.post(
                f"{self.firecrawl_base_url}/scrape",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('data', {})
                
                scraped_content = content.get('markdown', '') or content.get('html', '')
                
                if scraped_content:
                    # Analyze content with AI
                    analysis = self.analyze_content(scraped_content, url)
                    
                    return {
                        'success': True,
                        'url': url,
                        'method': 'Firecrawl',
                        'content': scraped_content,
                        'metadata': content.get('metadata', {}),
                        'analysis': analysis,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {'success': False, 'error': 'No content extracted'}
            else:
                return {'success': False, 'error': f'Firecrawl API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Firecrawl scraping error: {e}")
            return {'success': False, 'error': str(e)}
    
    def scrape_with_beautifulsoup(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape website using BeautifulSoup"""
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract content
            content = soup.get_text(strip=True)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True)[:20]:  # Limit to first 20 links
                links.append({
                    'url': urljoin(url, link['href']),
                    'text': link.get_text(strip=True)
                })
            
            # Analyze content
            analysis = self.analyze_content(content, url)
            
            return {
                'success': True,
                'url': url,
                'method': 'BeautifulSoup',
                'content': content,
                'links': links,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"BeautifulSoup scraping error: {e}")
            return {'success': False, 'error': str(e)}
    
    def find_documents(self, url: str, doc_types: List[str] = None) -> Dict[str, Any]:
        """Find documents on a website"""
        
        if not doc_types:
            doc_types = ['pdf', 'doc', 'docx']
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            documents = []
            
            for doc_type in doc_types:
                links = soup.find_all('a', href=re.compile(f'\\.{doc_type}', re.I))
                
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        filename = os.path.basename(href)
                        
                        documents.append({
                            'url': full_url,
                            'filename': filename,
                            'type': doc_type.upper(),
                            'link_text': link.get_text(strip=True),
                            'found_on': url
                        })
            
            return {
                'success': True,
                'url': url,
                'documents_found': len(documents),
                'documents': documents,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document finding error: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_content(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze scraped content with AI"""
        
        try:
            # Truncate content if too long
            if len(content) > 4000:
                content = content[:4000] + "... [truncated]"
            
            prompt = f"""
Analyze the following web content and provide a legal analysis:

Website URL: {url}
Content: {content}

Provide analysis in JSON format:
{{
    "content_type": "legal_document|news_article|court_record|regulation|general",
    "key_topics": ["topic1", "topic2", "topic3"],
    "legal_relevance": "high|medium|low",
    "summary": "Brief summary of main content",
    "legal_entities": ["entity1", "entity2"],
    "important_dates": ["date1", "date2"],
    "legal_concepts": ["concept1", "concept2"],
    "credibility_score": 0.8,
    "potential_risks": ["risk1", "risk2"]
}}

Analysis:
"""
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.analysis_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                
                try:
                    # Try to extract JSON from response
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        analysis = json.loads(json_str)
                    else:
                        analysis = {"summary": result[:300]}
                    
                    analysis['word_count'] = len(content.split())
                    analysis['analysis_timestamp'] = datetime.now().isoformat()
                    return analysis
                except json.JSONDecodeError:
                    return {
                        "content_type": "general",
                        "summary": result[:300],
                        "legal_relevance": "medium",
                        "word_count": len(content.split()),
                        "analysis_timestamp": datetime.now().isoformat()
                    }
            else:
                return {"error": "Analysis failed", "analysis_timestamp": datetime.now().isoformat()}
                
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return {"error": str(e), "analysis_timestamp": datetime.now().isoformat()}
    
    def test_firecrawl_connection(self) -> bool:
        """Test Firecrawl API connection"""
        if not self.firecrawl_api_key:
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.firecrawl_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.firecrawl_base_url}/scrape",
                headers=headers,
                json={'url': 'https://example.com'},
                timeout=10
            )
            
            return response.status_code in [200, 402]  # 402 = valid key, quota exceeded
        except Exception as e:
            logger.error(f"Firecrawl connection test failed: {e}")
            return False
    
    def test_ollama_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    def scrape_url(self, url: str, method: str = 'auto', options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main scraping method with automatic fallback"""
        
        if method == 'auto':
            # Try Firecrawl first if available
            if self.firecrawl_api_key and self.test_firecrawl_connection():
                result = self.scrape_with_firecrawl(url, options)
                if result['success']:
                    return result
            
            # Fallback to BeautifulSoup
            return self.scrape_with_beautifulsoup(url, options)
        
        elif method == 'firecrawl':
            return self.scrape_with_firecrawl(url, options)
        
        elif method == 'beautifulsoup':
            return self.scrape_with_beautifulsoup(url, options)
        
        else:
            return {'success': False, 'error': f'Unknown scraping method: {method}'}
    
    def get_scraping_status(self) -> Dict[str, Any]:
        """Get status of scraping services"""
        return {
            'firecrawl_available': self.test_firecrawl_connection(),
            'ollama_available': self.test_ollama_connection(),
            'firecrawl_api_key_configured': bool(self.firecrawl_api_key),
            'ollama_url': self.ollama_base_url,
            'analysis_model': self.analysis_model
        }

# Convenience function to create a scraping manager instance
def create_scraping_manager(config: Dict[str, Any] = None) -> WebScrapingManager:
    """Create a new WebScrapingManager instance"""
    return WebScrapingManager(config)

# Test function
def test_scraping_manager():
    """Test the scraping manager functionality"""
    print("🧪 Testing Web Scraping Manager...")
    
    from src.utils.config import load_config
    
    # Load project configuration
    config = load_config('config/config.yaml')
    manager = WebScrapingManager(config)
    
    # Test connections
    print(f"📡 Firecrawl URL: {manager.firecrawl_base_url}")
    print(f"🤖 Ollama URL: {manager.ollama_base_url}")
    print(f"📊 Analysis Model: {manager.analysis_model}")
    
    # Test Firecrawl
    if manager.test_firecrawl_connection():
        print("✅ Firecrawl connection successful")
    else:
        print("❌ Firecrawl connection failed")
    
    # Test Ollama
    if manager.test_ollama_connection():
        print("✅ Ollama connection successful")
    else:
        print("❌ Ollama connection failed")
    
    # Test scraping with a simple URL
    test_url = "https://example.com"
    print(f"\n🔍 Testing scraping with: {test_url}")
    
    result = manager.scrape_url(test_url, method='beautifulsoup')
    
    if result['success']:
        print("✅ Scraping successful")
        print(f"   Method: {result['method']}")
        print(f"   Content length: {len(result['content'])} characters")
        print(f"   Analysis available: {'analysis' in result}")
    else:
        print(f"❌ Scraping failed: {result['error']}")
    
    print("\n✅ Web Scraping Manager test completed!")

if __name__ == "__main__":
    test_scraping_manager()
