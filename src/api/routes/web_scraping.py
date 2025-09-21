"""
FastAPI routes for Web Scraping functionality
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from src.core.scraping.scraping_manager import WebScrapingManager
from src.utils.config import load_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/web-scraping", tags=["web-scraping"])

# Pydantic models
class ScrapeRequest(BaseModel):
    url: str
    method: str = "auto"  # auto, firecrawl, beautifulsoup
    options: Optional[Dict[str, Any]] = None

class DocumentSearchRequest(BaseModel):
    url: str
    doc_types: Optional[List[str]] = ["pdf", "doc", "docx", "txt"]

class BatchScrapeRequest(BaseModel):
    urls: List[str]
    method: str = "auto"
    options: Optional[Dict[str, Any]] = None

class LegalAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "legal_relevance"  # legal_relevance, case_analysis, document_classification

# Global instance - initialized with project configuration
config = load_config('config/config.yaml')
scraping_manager = WebScrapingManager(config)

@router.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    """Scrape a website using specified method"""
    
    try:
        result = scraping_manager.scrape_url(
            url=request.url,
            method=request.method,
            options=request.options
        )
        
        if result['success']:
            return {
                "success": True,
                "url": result['url'],
                "method": result['method'],
                "content": result['content'],
                "content_length": len(result['content']),
                "analysis": result.get('analysis', {}),
                "metadata": result.get('metadata', {}),
                "links": result.get('links', []),
                "timestamp": result['timestamp']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-documents")
async def find_documents(request: DocumentSearchRequest):
    """Find documents on a website"""
    
    try:
        result = scraping_manager.find_documents(request.url, request.doc_types)
        
        if result['success']:
            return {
                "success": True,
                "url": result['url'],
                "documents_found": result['documents_found'],
                "documents": result['documents'],
                "timestamp": result['timestamp']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-scrape")
async def batch_scrape(request: BatchScrapeRequest):
    """Scrape multiple websites in batch"""
    
    try:
        results = []
        errors = []
        
        for url in request.urls:
            try:
                result = scraping_manager.scrape_url(
                    url=url,
                    method=request.method,
                    options=request.options
                )
                
                if result['success']:
                    results.append({
                        "url": url,
                        "success": True,
                        "content_length": len(result['content']),
                        "method": result['method'],
                        "analysis": result.get('analysis', {}),
                        "timestamp": result['timestamp']
                    })
                else:
                    errors.append({
                        "url": url,
                        "error": result['error']
                    })
                    
            except Exception as e:
                errors.append({
                    "url": url,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_urls": len(request.urls),
            "successful_scrapes": len(results),
            "failed_scrapes": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Batch scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/legal-analysis")
async def legal_analysis(request: LegalAnalysisRequest):
    """Perform specialized legal analysis on scraped content"""
    
    try:
        # First scrape the content
        scrape_result = scraping_manager.scrape_url(request.url)
        
        if not scrape_result['success']:
            raise HTTPException(status_code=400, detail=f"Failed to scrape content: {scrape_result['error']}")
        
        content = scrape_result['content']
        analysis = scrape_result.get('analysis', {})
        
        # Enhance analysis based on type
        if request.analysis_type == "case_analysis":
            enhanced_analysis = {
                **analysis,
                "case_indicators": _analyze_case_indicators(content),
                "legal_entities": _extract_legal_entities(content),
                "case_status": _determine_case_status(content),
                "jurisdiction": _extract_jurisdiction(content)
            }
        elif request.analysis_type == "document_classification":
            enhanced_analysis = {
                **analysis,
                "document_type": _classify_document_type(content),
                "legal_domain": _identify_legal_domain(content),
                "compliance_requirements": _identify_compliance_requirements(content)
            }
        else:  # legal_relevance
            enhanced_analysis = {
                **analysis,
                "relevance_score": _calculate_relevance_score(content),
                "key_legal_concepts": _extract_legal_concepts(content),
                "risk_assessment": _assess_legal_risks(content)
            }
        
        return {
            "success": True,
            "url": request.url,
            "analysis_type": request.analysis_type,
            "content_length": len(content),
            "enhanced_analysis": enhanced_analysis,
            "timestamp": scrape_result['timestamp']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Legal analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-firecrawl")
async def test_firecrawl():
    """Test Firecrawl API connection"""
    
    try:
        is_available = scraping_manager.test_firecrawl_connection()
        return {
            "firecrawl_available": is_available,
            "api_key_configured": bool(scraping_manager.firecrawl_api_key),
            "base_url": scraping_manager.firecrawl_base_url
        }
        
    except Exception as e:
        logger.error(f"Firecrawl test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-ollama")
async def test_ollama():
    """Test Ollama connection for content analysis"""
    
    try:
        is_available = scraping_manager.test_ollama_connection()
        return {
            "ollama_available": is_available,
            "base_url": scraping_manager.ollama_base_url,
            "analysis_model": scraping_manager.analysis_model
        }
        
    except Exception as e:
        logger.error(f"Ollama test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraping-status")
async def get_scraping_status():
    """Get comprehensive scraping services status"""
    
    try:
        status = scraping_manager.get_scraping_status()
        return {
            "success": True,
            "status": status,
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/legal-targets")
async def get_legal_targets():
    """Get sample legal websites for scraping"""
    
    legal_targets = {
        "government": [
            {
                "name": "SEC Litigation",
                "url": "https://www.sec.gov/litigation",
                "description": "Securities litigation releases",
                "category": "Securities Law"
            },
            {
                "name": "FTC Legal Library",
                "url": "https://www.ftc.gov/legal-library",
                "description": "Federal Trade Commission legal resources",
                "category": "Consumer Protection"
            },
            {
                "name": "DOJ Press Releases",
                "url": "https://www.justice.gov/news",
                "description": "Department of Justice legal news",
                "category": "Criminal Law"
            }
        ],
        "legal_databases": [
            {
                "name": "Justia Cases",
                "url": "https://law.justia.com/cases/",
                "description": "Free legal case database",
                "category": "Case Law"
            },
            {
                "name": "FindLaw Cases",
                "url": "https://caselaw.findlaw.com/",
                "description": "Comprehensive case law database",
                "category": "Case Law"
            },
            {
                "name": "Court Listener",
                "url": "https://www.courtlistener.com/",
                "description": "Free legal search engine",
                "category": "Case Law"
            }
        ],
        "legal_news": [
            {
                "name": "Law.com",
                "url": "https://www.law.com/",
                "description": "Legal news and analysis",
                "category": "Legal News"
            },
            {
                "name": "ABA Journal",
                "url": "https://www.abajournal.com/",
                "description": "American Bar Association news",
                "category": "Legal News"
            }
        ],
        "regulatory": [
            {
                "name": "Federal Register",
                "url": "https://www.federalregister.gov/",
                "description": "Federal regulations and notices",
                "category": "Regulatory"
            },
            {
                "name": "CFR Online",
                "url": "https://www.ecfr.gov/",
                "description": "Code of Federal Regulations",
                "category": "Regulatory"
            }
        ]
    }
    
    return {
        "success": True,
        "legal_targets": legal_targets,
        "total_categories": len(legal_targets),
        "total_targets": sum(len(targets) for targets in legal_targets.values())
    }

@router.get("/sample-scraping-queries")
async def get_sample_scraping_queries():
    """Get sample scraping queries for legal research"""
    
    sample_queries = [
        {
            "query": "Scrape SEC enforcement actions from the last 30 days",
            "url": "https://www.sec.gov/litigation",
            "method": "firecrawl",
            "analysis_type": "case_analysis"
        },
        {
            "query": "Find all PDF documents on a legal firm's website",
            "url": "https://example-law-firm.com",
            "method": "beautifulsoup",
            "analysis_type": "document_classification"
        },
        {
            "query": "Analyze recent court decisions for employment law",
            "url": "https://law.justia.com/cases/",
            "method": "auto",
            "analysis_type": "legal_relevance"
        },
        {
            "query": "Scrape regulatory updates from Federal Register",
            "url": "https://www.federalregister.gov/",
            "method": "firecrawl",
            "analysis_type": "document_classification"
        }
    ]
    
    return {
        "success": True,
        "sample_queries": sample_queries,
        "total_queries": len(sample_queries)
    }

# Helper functions for legal analysis
def _analyze_case_indicators(content: str) -> List[str]:
    """Analyze content for case-related indicators"""
    case_indicators = []
    content_lower = content.lower()
    
    if "plaintiff" in content_lower or "defendant" in content_lower:
        case_indicators.append("litigation_case")
    if "settlement" in content_lower or "settled" in content_lower:
        case_indicators.append("settlement")
    if "judgment" in content_lower or "ruling" in content_lower:
        case_indicators.append("court_decision")
    if "appeal" in content_lower or "appellate" in content_lower:
        case_indicators.append("appellate_case")
    
    return case_indicators

def _extract_legal_entities(content: str) -> List[str]:
    """Extract legal entities from content"""
    # Simple entity extraction - in production, use NER
    entities = []
    content_lower = content.lower()
    
    if "court" in content_lower:
        entities.append("court")
    if "attorney" in content_lower or "lawyer" in content_lower:
        entities.append("attorney")
    if "judge" in content_lower:
        entities.append("judge")
    if "jury" in content_lower:
        entities.append("jury")
    
    return entities

def _determine_case_status(content: str) -> str:
    """Determine case status from content"""
    content_lower = content.lower()
    
    if "pending" in content_lower or "ongoing" in content_lower:
        return "pending"
    elif "settled" in content_lower or "settlement" in content_lower:
        return "settled"
    elif "dismissed" in content_lower:
        return "dismissed"
    elif "judgment" in content_lower or "ruling" in content_lower:
        return "decided"
    else:
        return "unknown"

def _extract_jurisdiction(content: str) -> str:
    """Extract jurisdiction from content"""
    content_lower = content.lower()
    
    if "federal" in content_lower or "u.s." in content_lower:
        return "federal"
    elif "state" in content_lower:
        return "state"
    elif "district" in content_lower:
        return "district"
    else:
        return "unknown"

def _classify_document_type(content: str) -> str:
    """Classify document type"""
    content_lower = content.lower()
    
    if "contract" in content_lower or "agreement" in content_lower:
        return "contract"
    elif "brief" in content_lower or "motion" in content_lower:
        return "legal_brief"
    elif "opinion" in content_lower or "decision" in content_lower:
        return "court_opinion"
    elif "regulation" in content_lower or "rule" in content_lower:
        return "regulation"
    else:
        return "general_legal_document"

def _identify_legal_domain(content: str) -> str:
    """Identify legal domain"""
    content_lower = content.lower()
    
    if "criminal" in content_lower or "criminal law" in content_lower:
        return "criminal_law"
    elif "civil" in content_lower or "civil law" in content_lower:
        return "civil_law"
    elif "corporate" in content_lower or "business" in content_lower:
        return "corporate_law"
    elif "employment" in content_lower or "labor" in content_lower:
        return "employment_law"
    else:
        return "general_law"

def _identify_compliance_requirements(content: str) -> List[str]:
    """Identify compliance requirements"""
    requirements = []
    content_lower = content.lower()
    
    if "gdpr" in content_lower or "privacy" in content_lower:
        requirements.append("gdpr_compliance")
    if "sox" in content_lower or "sarbanes" in content_lower:
        requirements.append("sox_compliance")
    if "hipaa" in content_lower or "health" in content_lower:
        requirements.append("hipaa_compliance")
    
    return requirements

def _calculate_relevance_score(content: str) -> float:
    """Calculate legal relevance score"""
    content_lower = content.lower()
    score = 0.0
    
    legal_terms = ["law", "legal", "court", "judge", "attorney", "litigation", "case", "ruling"]
    for term in legal_terms:
        if term in content_lower:
            score += 0.1
    
    return min(score, 1.0)

def _extract_legal_concepts(content: str) -> List[str]:
    """Extract legal concepts"""
    concepts = []
    content_lower = content.lower()
    
    if "liability" in content_lower:
        concepts.append("liability")
    if "negligence" in content_lower:
        concepts.append("negligence")
    if "breach" in content_lower:
        concepts.append("breach_of_contract")
    if "damages" in content_lower:
        concepts.append("damages")
    
    return concepts

def _assess_legal_risks(content: str) -> List[str]:
    """Assess legal risks"""
    risks = []
    content_lower = content.lower()
    
    if "violation" in content_lower or "breach" in content_lower:
        risks.append("compliance_violation")
    if "penalty" in content_lower or "fine" in content_lower:
        risks.append("financial_penalty")
    if "litigation" in content_lower or "lawsuit" in content_lower:
        risks.append("litigation_risk")
    
    return risks
