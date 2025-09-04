"""
DALI Legal AI - Firecrawl Web Scraper Module
Handles intelligent web scraping for legal research using Firecrawl
"""

import os
import logging
import time
from typing import List, Dict, Optional, Union
from urllib.parse import urljoin, urlparse
import requests
from firecrawl import FirecrawlApp
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class ScrapedDocument:
    """Data class for scraped document results"""
    url: str
    title: str
    content: str
    metadata: Dict
    success: bool
    error: Optional[str] = None


class FirecrawlScraper:
    """
    Firecrawl Web Scraper for DALI Legal AI System
    Provides intelligent web scraping capabilities for legal research
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        
        if not self.api_key:
            logger.warning("No Firecrawl API key provided. Some features may be limited.")
            self.app = None
        else:
            try:
                self.app = FirecrawlApp(api_key=self.api_key)
                logger.info("Firecrawl initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firecrawl: {e}")
                self.app = None
    
    def scrape_url(
        self,
        url: str,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        wait_for: Optional[int] = None,
        timeout: int = 30000
    ) -> ScrapedDocument:
        """
        Scrape a single URL using Firecrawl
        
        Args:
            url: URL to scrape
            include_tags: HTML tags to include in scraping
            exclude_tags: HTML tags to exclude from scraping
            wait_for: Time to wait for page load (milliseconds)
            timeout: Request timeout (milliseconds)
            
        Returns:
            ScrapedDocument with results
        """
        if not self.app:
            return self._fallback_scrape(url)
        
        try:
            # Configure scraping options
            scrape_options = {
                'formats': ['markdown', 'html'],
                'timeout': timeout,
                'waitFor': wait_for or 3000,
                'includeTags': include_tags or ['article', 'main', 'content', 'div', 'p', 'h1', 'h2', 'h3'],
                'excludeTags': exclude_tags or ['nav', 'footer', 'header', 'aside', 'script', 'style', 'ads']
            }
            
            # Perform scraping
            result = self.app.scrape_url(url, params=scrape_options)
            
            if result.get('success'):
                return ScrapedDocument(
                    url=url,
                    title=result.get('data', {}).get('title', 'Unknown Title'),
                    content=result.get('data', {}).get('markdown', ''),
                    metadata={
                        'description': result.get('data', {}).get('description', ''),
                        'keywords': result.get('data', {}).get('keywords', []),
                        'author': result.get('data', {}).get('author', ''),
                        'language': result.get('data', {}).get('language', ''),
                        'scraped_at': time.time(),
                        'source_url': url,
                        'scraper': 'firecrawl'
                    },
                    success=True
                )
            else:
                error_msg = result.get('error', 'Unknown scraping error')
                logger.error(f"Firecrawl scraping failed for {url}: {error_msg}")
                return ScrapedDocument(
                    url=url,
                    title='',
                    content='',
                    metadata={},
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Error scraping {url} with Firecrawl: {e}")
            return self._fallback_scrape(url)
    
    def scrape_multiple_urls(
        self,
        urls: List[str],
        batch_size: int = 5,
        delay_between_requests: float = 1.0
    ) -> List[ScrapedDocument]:
        """
        Scrape multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to scrape
            batch_size: Number of URLs to process in parallel
            delay_between_requests: Delay between requests (seconds)
            
        Returns:
            List of ScrapedDocument results
        """
        results = []
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            for url in batch:
                result = self.scrape_url(url)
                results.append(result)
                
                # Rate limiting
                if delay_between_requests > 0:
                    time.sleep(delay_between_requests)
            
            logger.info(f"Completed batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}")
        
        return results
    
    def crawl_website(
        self,
        base_url: str,
        max_pages: int = 10,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ) -> List[ScrapedDocument]:
        """
        Crawl an entire website or specific sections
        
        Args:
            base_url: Base URL to start crawling from
            max_pages: Maximum number of pages to crawl
            include_paths: URL patterns to include
            exclude_paths: URL patterns to exclude
            
        Returns:
            List of ScrapedDocument results
        """
        if not self.app:
            logger.error("Firecrawl not available for website crawling")
            return []
        
        try:
            crawl_options = {
                'limit': max_pages,
                'scrapeOptions': {
                    'formats': ['markdown'],
                    'includeTags': ['article', 'main', 'content', 'div', 'p', 'h1', 'h2', 'h3'],
                    'excludeTags': ['nav', 'footer', 'header', 'aside', 'script', 'style']
                }
            }
            
            if include_paths:
                crawl_options['includePaths'] = include_paths
            if exclude_paths:
                crawl_options['excludePaths'] = exclude_paths
            
            # Start crawling
            crawl_result = self.app.crawl_url(base_url, params=crawl_options)
            
            if crawl_result.get('success'):
                results = []
                for page_data in crawl_result.get('data', []):
                    result = ScrapedDocument(
                        url=page_data.get('url', base_url),
                        title=page_data.get('title', 'Unknown Title'),
                        content=page_data.get('markdown', ''),
                        metadata={
                            'description': page_data.get('description', ''),
                            'keywords': page_data.get('keywords', []),
                            'scraped_at': time.time(),
                            'source_url': page_data.get('url', base_url),
                            'scraper': 'firecrawl_crawl'
                        },
                        success=True
                    )
                    results.append(result)
                
                logger.info(f"Successfully crawled {len(results)} pages from {base_url}")
                return results
            else:
                logger.error(f"Crawling failed for {base_url}: {crawl_result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error crawling {base_url}: {e}")
            return []
    
    def search_legal_databases(
        self,
        query: str,
        databases: Optional[List[str]] = None
    ) -> List[ScrapedDocument]:
        """
        Search legal databases and government websites
        
        Args:
            query: Search query
            databases: List of database URLs to search
            
        Returns:
            List of ScrapedDocument results
        """
        if databases is None:
            # Default Saudi Arabian legal databases and government sites
            databases = [
                "https://laws.boe.gov.sa",  # Saudi Board of Experts
                "https://www.moj.gov.sa",   # Ministry of Justice
                "https://nca.gov.sa",       # National Cybersecurity Authority
                "https://sdaia.gov.sa"      # Saudi Data & AI Authority
            ]
        
        results = []
        
        for db_url in databases:
            try:
                # Construct search URL (this would need to be customized per database)
                search_url = f"{db_url}/search?q={query}"
                
                # Scrape search results
                result = self.scrape_url(search_url)
                if result.success:
                    result.metadata['search_query'] = query
                    result.metadata['database'] = db_url
                    results.append(result)
                
            except Exception as e:
                logger.error(f"Error searching {db_url}: {e}")
        
        return results
    
    def _fallback_scrape(self, url: str) -> ScrapedDocument:
        """
        Fallback scraping method using requests and basic parsing
        Used when Firecrawl is not available
        """
        try:
            headers = {
                'User-Agent': 'DALI Legal AI Research Bot 1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Basic content extraction (would need BeautifulSoup for better parsing)
            content = response.text
            
            # Extract title (basic regex)
            import re
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else 'Unknown Title'
            
            # Remove HTML tags (basic cleaning)
            clean_content = re.sub(r'<[^>]+>', ' ', content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            return ScrapedDocument(
                url=url,
                title=title,
                content=clean_content[:5000],  # Limit content length
                metadata={
                    'scraped_at': time.time(),
                    'source_url': url,
                    'scraper': 'fallback',
                    'content_length': len(clean_content)
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"Fallback scraping failed for {url}: {e}")
            return ScrapedDocument(
                url=url,
                title='',
                content='',
                metadata={},
                success=False,
                error=str(e)
            )
    
    def extract_legal_citations(self, content: str) -> List[Dict]:
        """
        Extract legal citations from scraped content
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of extracted citations with metadata
        """
        citations = []
        
        # Saudi legal citation patterns
        patterns = {
            'royal_decree': r'المرسوم الملكي رقم\s*([م/\d]+)',
            'ministerial_decision': r'قرار وزاري رقم\s*(\d+)',
            'law_number': r'نظام رقم\s*(\d+)',
            'regulation': r'لائحة رقم\s*(\d+)'
        }
        
        import re
        for citation_type, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                citations.append({
                    'type': citation_type,
                    'reference': match,
                    'context': self._extract_context(content, match)
                })
        
        return citations
    
    def _extract_context(self, content: str, reference: str, context_length: int = 200) -> str:
        """Extract context around a legal reference"""
        import re
        
        # Find the position of the reference
        match = re.search(re.escape(reference), content, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context_length // 2)
            end = min(len(content), match.end() + context_length // 2)
            return content[start:end].strip()
        
        return ""
    
    def health_check(self) -> bool:
        """Check if Firecrawl service is available"""
        if not self.app:
            return False
        
        try:
            # Test with a simple URL
            test_result = self.app.scrape_url("https://httpbin.org/html")
            return test_result.get('success', False)
        except Exception as e:
            logger.error(f"Firecrawl health check failed: {e}")
            return False


# Utility functions
def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text content"""
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def is_legal_website(url: str) -> bool:
    """Check if URL appears to be from a legal website"""
    legal_domains = [
        'gov.sa', 'moj.gov.sa', 'laws.boe.gov.sa', 'nca.gov.sa',
        'westlaw.com', 'lexisnexis.com', 'justia.com',
        'courtlistener.com', 'law.com'
    ]
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    return any(legal_domain in domain for legal_domain in legal_domains)


if __name__ == "__main__":
    # Example usage
    scraper = FirecrawlScraper()
    
    if scraper.health_check():
        print("✅ Firecrawl is available")
        
        # Test scraping a legal website
        result = scraper.scrape_url("https://laws.boe.gov.sa")
        if result.success:
            print(f"Successfully scraped: {result.title}")
            print(f"Content length: {len(result.content)}")
        else:
            print(f"Scraping failed: {result.error}")
    else:
        print("❌ Firecrawl not available, using fallback methods")

