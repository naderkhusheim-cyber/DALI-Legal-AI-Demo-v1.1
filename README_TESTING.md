# DALI Legal AI - Testing Package

This package contains comprehensive test data and scripts for testing the DALI Legal AI system's crawling and retrieval capabilities.

## 📦 Package Contents

### 1. **Sample Data Sources** (`sample_legal_data_sources.json`)
- **10 realistic Saudi Arabian legal data sources**
- Government websites, regulatory authorities, and legal databases
- Each source includes metadata, crawling strategies, and test queries
- Covers major legal domains: commercial, regulatory, cybersecurity, banking, etc.

### 2. **Sample Documents** (`sample_documents/`)
- **20 realistic legal documents** in various formats
- Document types: contracts, regulations, case law, legal opinions, compliance guides
- Generated with realistic Saudi Arabian legal content
- Includes document index with metadata

### 3. **Test Scripts**
- **`sample_test_script.py`**: Comprehensive test suite for the DALI system
- **`sample_documents_generator.py`**: Generator for additional test documents

## 🚀 Quick Start Testing

### Prerequisites
1. DALI Legal AI system installed and running
2. Python environment with required dependencies
3. Ollama running with a legal-focused model

### Running Tests

1. **Extract the test package**:
   ```bash
   tar -xzf dali_test_package.tar.gz
   cd dali_test_package
   ```

2. **Copy files to your DALI installation**:
   ```bash
   cp sample_legal_data_sources.json /path/to/dali-legal-ai/
   cp sample_test_script.py /path/to/dali-legal-ai/
   cp -r sample_documents /path/to/dali-legal-ai/
   ```

3. **Run the comprehensive test**:
   ```bash
   cd /path/to/dali-legal-ai
   python3 sample_test_script.py
   ```

## 📊 Test Data Sources Overview

| ID | Source | Type | Expected Docs | Content Focus |
|----|--------|------|---------------|---------------|
| 1 | Saudi Board of Experts | Government DB | 500 | Laws & Regulations |
| 2 | Ministry of Justice | Government Portal | 200 | Legal Procedures |
| 3 | SDAIA | Regulatory Authority | 50 | Data Protection |
| 4 | NCA | Cybersecurity Authority | 75 | Cybersecurity Law |
| 5 | SAMA | Financial Regulator | 300 | Banking Law |
| 6 | CMA | Securities Regulator | 150 | Securities Law |
| 7 | GAC | Competition Authority | 100 | Competition Law |
| 8 | Ministry of Commerce | Commercial Authority | 250 | Commercial Law |
| 9 | Ministry of HR | Labor Authority | 180 | Employment Law |
| 10 | ZATCA | Tax Authority | 200 | Tax Law |

## 🧪 Test Scenarios

### 1. **Basic Legal Research**
- **Query**: "What are the requirements for establishing a company in Saudi Arabia?"
- **Expected Sources**: Board of Experts, Ministry of Justice, Ministry of Commerce
- **Expected Results**: 10+ relevant documents

### 2. **Data Protection Compliance**
- **Query**: "PDPL compliance requirements for international data transfers"
- **Expected Sources**: SDAIA, NCA
- **Expected Results**: 5+ relevant documents

### 3. **Financial Regulations**
- **Query**: "Banking license application process and requirements"
- **Expected Sources**: SAMA, CMA
- **Expected Results**: 8+ relevant documents

### 4. **Employment Law**
- **Query**: "Employee termination procedures and severance requirements"
- **Expected Sources**: Ministry of HR
- **Expected Results**: 6+ relevant documents

### 5. **Tax Compliance**
- **Query**: "VAT registration thresholds for small businesses"
- **Expected Sources**: ZATCA
- **Expected Results**: 4+ relevant documents

## 📄 Sample Document Types

### Contracts (4 documents)
- Commercial services agreements
- Realistic Saudi Arabian legal language
- Various industries and scenarios

### Regulations (6 documents)
- Ministry-issued regulations
- Proper legal structure and formatting
- Different regulatory domains

### Case Law (4 documents)
- Commercial court decisions
- Realistic legal reasoning and citations
- Saudi Arabian judicial format

### Legal Opinions (2 documents)
- Professional legal analysis
- Corporate governance and compliance focus
- Law firm format and structure

### Compliance Guides (4 documents)
- Regulatory authority guidance
- Practical compliance checklists
- Implementation timelines

## 🔧 Customizing Tests

### Adding New Data Sources
Edit `sample_legal_data_sources.json`:
```json
{
  "id": 11,
  "name": "Your Legal Source",
  "url": "https://example.com",
  "type": "source_type",
  "jurisdiction": "Saudi Arabia",
  "content_type": "content_category"
}
```

### Generating More Documents
Run the document generator:
```bash
python3 sample_documents_generator.py
```

### Custom Test Scenarios
Modify the test scenarios in `sample_legal_data_sources.json`:
```json
{
  "scenario": "Your Test Scenario",
  "query": "Your legal question",
  "expected_sources": [1, 2, 3],
  "expected_result_count": 5
}
```

## 📈 Expected Test Results

### Crawling Performance
- **Success Rate**: 70-90% (depending on website availability)
- **Content Extraction**: 1000-5000 characters per page
- **Processing Time**: 2-5 seconds per page

### Search Accuracy
- **Relevance Score**: 0.7+ for top results
- **Response Time**: <2 seconds for vector search
- **LLM Analysis**: 10-30 seconds for comprehensive legal research

### System Integration
- **Document Processing**: Support for PDF, DOCX, TXT formats
- **Vector Storage**: Automatic chunking and embedding
- **Knowledge Base**: Semantic search across all content

## 🛠️ Troubleshooting

### Common Issues

1. **Crawling Failures**
   - Check internet connectivity
   - Verify Firecrawl API key (if using)
   - Some government sites may block automated requests

2. **Search Returns No Results**
   - Ensure documents are properly indexed
   - Check vector store configuration
   - Verify embedding model is loaded

3. **LLM Not Responding**
   - Confirm Ollama is running
   - Check model is downloaded
   - Verify network connectivity to Ollama

### Performance Optimization

1. **Batch Processing**
   - Process documents in smaller batches
   - Adjust delay between requests
   - Monitor system resources

2. **Vector Store Tuning**
   - Optimize chunk size for your content
   - Adjust similarity thresholds
   - Consider different embedding models

## 📞 Support

For issues with the test package:
- Check the main DALI repository documentation
- Review system logs for error details
- Ensure all dependencies are properly installed

## 🎯 Success Metrics

A successful test run should achieve:
- ✅ 80%+ crawling success rate
- ✅ Sub-second vector search response times
- ✅ Relevant results for all test scenarios
- ✅ Proper document processing and indexing
- ✅ Functional LLM integration

---

**Happy Testing! 🚀**

*This test package is designed to validate the core functionality of the DALI Legal AI system with realistic Saudi Arabian legal content.*

