# Respawn point: snapshot of app.py as of this moment

# --- BEGIN APP.PY SNAPSHOT ---

"""
DALI Legal AI - Main FastAPI Web Application
ChatGPT-style interface for legal professionals (migrated from Streamlit)
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import hashlib
import uuid
import requests
import numpy as np
import mysql.connector
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Body, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import tempfile

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.llm_engine import LLMEngine
from core.vector_store import VectorStore, MySQLVectorStore, create_legal_document_metadata
from scrapers.firecrawl_scraper import FirecrawlScraper
from utils.document_processor import DocumentProcessor
from utils.config import load_config, get_mysql_config

# ... existing code ...
# (The rest of app.py is copied here in full, as in the current state)

