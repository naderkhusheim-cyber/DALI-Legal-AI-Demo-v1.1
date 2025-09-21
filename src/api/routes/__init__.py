"""
API routes package for DALI Legal AI
"""

from .knowledge_base import router as knowledge_base_router
from .web_scraping import router as web_scraping_router

__all__ = ['knowledge_base_router', 'web_scraping_router']
