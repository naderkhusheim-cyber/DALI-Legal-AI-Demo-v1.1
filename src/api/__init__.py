"""
API package for DALI Legal AI
"""

from .routes.knowledge_base import router as knowledge_base_router
from .routes.web_scraping import router as web_scraping_router

__all__ = ['knowledge_base_router', 'web_scraping_router']
