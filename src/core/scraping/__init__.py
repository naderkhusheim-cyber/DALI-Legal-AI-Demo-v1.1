"""
Web Scraping package for DALI Legal AI
"""

from .scraping_manager import WebScrapingManager, create_scraping_manager

# Import FirecrawlScraper from the correct location
try:
    from ..scrapers.firecrawl_scraper import FirecrawlScraper
    __all__ = ['WebScrapingManager', 'create_scraping_manager', 'FirecrawlScraper']
except ImportError:
    __all__ = ['WebScrapingManager', 'create_scraping_manager']
