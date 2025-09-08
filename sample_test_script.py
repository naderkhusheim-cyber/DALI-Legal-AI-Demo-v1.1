#!/usr/bin/env python3
"""
DALI Legal AI - Sample Data Sources Test Script
Tests crawling and retrieval capabilities with realistic legal data sources
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add the src directory to the path for imports
sys.path.append('src')

from core.llm_engine import LLMEngine
from core.vector_store import VectorStore, create_legal_document_metadata
from scrapers.firecrawl_scraper import FirecrawlScraper
from utils.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DALITestSuite:
    """Test suite for DALI Legal AI system with sample data sources"""
    
    def __init__(self):
        self.config = get_config()
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'crawled_sources': [],
            'search_results': [],
            'errors': []
        }
        
        # Initialize components
        try:
            self.llm_engine = LLMEngine()
            self.vector_store = VectorStore()
            self.scraper = FirecrawlScraper()
            logger.info("✅ All components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    def load_sample_data_sources(self, file_path: str = 'sample_legal_data_sources.json'):
        """Load sample data sources from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.data_sources = data['dali_legal_ai_sample_data_sources']['data_sources']
            self.crawling_config = data['dali_legal_ai_sample_data_sources']['crawling_configuration']
            self.test_scenarios = data['dali_legal_ai_sample_data_sources']['testing_scenarios']
            
            logger.info(f"✅ Loaded {len(self.data_sources)} sample data sources")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load sample data sources: {e}")
            return False
    
    def test_single_source_crawl(self, source_id: int, max_pages: int = 5):
        """Test crawling a single data source"""
        try:
            source = next((s for s in self.data_sources if s['id'] == source_id), None)
            if not source:
                raise ValueError(f"Source ID {source_id} not found")
            
            logger.info(f"🕷️ Testing crawl of: {source['name']}")
            
            # Perform crawling
            result = self.scraper.scrape_url(source['url'])
            
            if result.success:
                # Add to vector store
                metadata = create_legal_document_metadata(
                    title=source['name'],
                    document_type=source['content_type'],
                    source=source['url'],
                    jurisdiction=source['jurisdiction'],
                    practice_area=source['type']
                )
                
                doc_ids = self.vector_store.add_document(result.content, metadata)
                
                crawl_result = {
                    'source_id': source_id,
                    'source_name': source['name'],
                    'url': source['url'],
                    'success': True,
                    'content_length': len(result.content),
                    'document_ids': doc_ids,
                    'chunks_created': len(doc_ids)
                }
                
                self.results['crawled_sources'].append(crawl_result)
                self.results['tests_passed'] += 1
                
                logger.info(f"✅ Successfully crawled {source['name']} - {len(doc_ids)} chunks created")
                return crawl_result
                
            else:
                error_msg = f"Crawling failed: {result.error}"
                logger.error(f"❌ {error_msg}")
                self.results['errors'].append({
                    'source_id': source_id,
                    'error': error_msg
                })
                self.results['tests_failed'] += 1
                return None
                
        except Exception as e:
            error_msg = f"Test failed for source {source_id}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append({
                'source_id': source_id,
                'error': error_msg
            })
            self.results['tests_failed'] += 1
            return None
        
        finally:
            self.results['tests_run'] += 1
    
    def test_search_scenario(self, scenario):
        """Test a search scenario"""
        try:
            logger.info(f"🔍 Testing search scenario: {scenario['scenario']}")
            
            # Perform vector search
            search_results = self.vector_store.search(
                scenario['query'],
                n_results=scenario['expected_result_count']
            )
            
            # Perform LLM research
            llm_response = self.llm_engine.legal_research(scenario['query'])
            
            search_result = {
                'scenario': scenario['scenario'],
                'query': scenario['query'],
                'vector_results_count': len(search_results),
                'expected_count': scenario['expected_result_count'],
                'llm_response_length': len(llm_response),
                'success': len(search_results) > 0,
                'top_results': [
                    {
                        'content_preview': r['content'][:200] + '...',
                        'score': r['score'],
                        'source': r['metadata'].get('source', 'Unknown')
                    }
                    for r in search_results[:3]  # Top 3 results
                ]
            }
            
            self.results['search_results'].append(search_result)
            
            if search_result['success']:
                self.results['tests_passed'] += 1
                logger.info(f"✅ Search scenario passed - found {len(search_results)} results")
            else:
                self.results['tests_failed'] += 1
                logger.warning(f"⚠️ Search scenario found no results")
            
            return search_result
            
        except Exception as e:
            error_msg = f"Search scenario failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append({
                'scenario': scenario['scenario'],
                'error': error_msg
            })
            self.results['tests_failed'] += 1
            return None
        
        finally:
            self.results['tests_run'] += 1
    
    def run_comprehensive_test(self, max_sources: int = 3):
        """Run comprehensive test suite"""
        logger.info("🚀 Starting DALI Legal AI comprehensive test suite")
        
        # Test crawling (limited number for demo)
        logger.info(f"📥 Testing crawling of {max_sources} sample sources...")
        for i, source in enumerate(self.data_sources[:max_sources]):
            self.test_single_source_crawl(source['id'])
        
        # Wait a moment for indexing
        import time
        time.sleep(2)
        
        # Test search scenarios
        logger.info("🔍 Testing search scenarios...")
        for scenario in self.test_scenarios:
            self.test_search_scenario(scenario)
        
        # Generate final report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.results['end_time'] = datetime.now().isoformat()
        self.results['success_rate'] = (
            self.results['tests_passed'] / self.results['tests_run'] * 100
            if self.results['tests_run'] > 0 else 0
        )
        
        # Save results to file
        report_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as file:
            json.dump(self.results, file, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 DALI LEGAL AI TEST RESULTS SUMMARY")
        print("="*60)
        print(f"📊 Tests Run: {self.results['tests_run']}")
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")
        print(f"📈 Success Rate: {self.results['success_rate']:.1f}%")
        print(f"🕷️ Sources Crawled: {len(self.results['crawled_sources'])}")
        print(f"🔍 Search Tests: {len(self.results['search_results'])}")
        print(f"📄 Report Saved: {report_file}")
        
        if self.results['errors']:
            print(f"\n⚠️ Errors Encountered: {len(self.results['errors'])}")
            for error in self.results['errors'][:3]:  # Show first 3 errors
                print(f"   - {error}")
        
        print("\n" + "="*60)
        
        return self.results


def main():
    """Main test execution function"""
    try:
        # Initialize test suite
        test_suite = DALITestSuite()
        
        # Load sample data sources
        if not test_suite.load_sample_data_sources():
            logger.error("Failed to load sample data sources")
            return 1
        
        # Run comprehensive test
        test_suite.run_comprehensive_test(max_sources=3)  # Test 3 sources for demo
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Test suite interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

