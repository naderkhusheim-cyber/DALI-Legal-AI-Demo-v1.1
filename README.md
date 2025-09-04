# DALI Legal AI System

**Development of Ambitious Leading Ideas (DALI)**  
*A venture building initiative by Siyada Tech*

## 🚀 Overview

DALI Legal AI is a lightweight, office-friendly legal AI system that combines the best open-source tools with zero-knowledge installation requirements. It's powerful enough for serious legal work, yet simple enough for your team to set up during lunch break.

### Arabic Name
**دالي - دائرة أفكار رائدة مبتكرة**  
*Da'irat Afkar Ra'ida Mubtakira*  
*Department of Leading Innovative Ideas*

## ✨ Key Features

- **🧠 Local LLM Processing**: Powered by Ollama with models like Llama 3 and Mistral
- **🕷️ Intelligent Web Scraping**: AI-powered data extraction with Firecrawl
- **📚 Vector Knowledge Base**: Semantic search with Chroma vector database
- **🌐 User-Friendly Interface**: Clean Streamlit web application
- **🔒 100% Privacy**: All data stays within your office infrastructure
- **⚡ 30-Minute Setup**: From zero to working legal AI in half an hour

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Law Firm                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Ollama    │  │  Firecrawl  │  │   Chroma    │    │
│  │ LLM Engine  │  │ Web Scraper │  │ Vector DB   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│           │               │               │            │
│           └───────────────┼───────────────┘            │
│                           │                            │
│                  ┌─────────────┐                       │
│                  │  Streamlit  │                       │
│                  │Web Interface│                       │
│                  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM Engine** | Ollama | Local language model processing |
| **Web Scraping** | Firecrawl | Intelligent legal data extraction |
| **Vector Database** | Chroma | Document embeddings and semantic search |
| **Web Interface** | Streamlit | User-friendly dashboard |
| **Document Processing** | LangChain | Text processing and chunking |
| **Embeddings** | SentenceTransformers | Text vectorization |

## 🚀 Quick Start

### Prerequisites

- **Hardware**: 8GB RAM minimum, any modern processor
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Storage**: 50GB free space

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/siyada-tech/dali-legal-ai.git
   cd dali-legal-ai
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Start the system**
   ```bash
   ./scripts/start.sh
   ```

4. **Access the interface**
   Open your browser to `http://localhost:8501`

### Manual Installation

If you prefer manual setup:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
pip install -r requirements.txt

# Download LLM model
ollama pull llama3

# Start the application
streamlit run src/web/app.py
```

## 📖 Usage

### Legal Research
1. Navigate to the "Research" tab
2. Enter your legal query in natural language
3. Review AI-generated research results with citations

### Document Analysis
1. Upload legal documents via the "Documents" tab
2. Ask questions about the document content
3. Extract key clauses and legal insights

### Knowledge Management
1. Build your firm's knowledge base in the "Knowledge" tab
2. Add case precedents and legal expertise
3. Search across all firm knowledge with semantic queries

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3

# Firecrawl Configuration
FIRECRAWL_API_KEY=your_api_key_here

# Chroma Configuration
CHROMA_PERSIST_DIRECTORY=./data/embeddings
CHROMA_COLLECTION_NAME=legal_documents

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
```

### Model Selection

Supported Ollama models:
- `llama3` (Recommended for general legal work)
- `mistral` (Good for contract analysis)
- `codellama` (For legal document generation)

## 🔒 Security & Compliance

### Data Protection
- **100% On-Premises**: All data processing happens locally
- **No External APIs**: Optional external scraping only
- **Encrypted Storage**: All documents encrypted at rest
- **Access Control**: Role-based permissions

### Compliance Features
- Attorney-client privilege protection
- Audit logging for all system interactions
- Data retention and deletion policies
- GDPR/CCPA compliance ready

## 📊 Performance Metrics

Expected improvements with DALI Legal AI:
- **70% reduction** in legal research time
- **85% reduction** in document review errors
- **90% client satisfaction** with faster response times
- **30% increase** in case capacity without additional staff

## 🤝 Contributing

We welcome contributions from the legal tech community!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Installation Guide](docs/installation.md)
- [User Manual](docs/user-guide.md)
- [API Documentation](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

### Community
- **Issues**: [GitHub Issues](https://github.com/siyada-tech/dali-legal-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/siyada-tech/dali-legal-ai/discussions)
- **Email**: dali@siyada.tech

## 🏢 About Siyada Tech

DALI is developed by Siyada Tech's venture building unit, focused on creating innovative solutions for the legal industry. We combine deep legal domain expertise with cutting-edge AI technology.

**Contact Information:**
- Website: [www.siyadatech.com](https://www.siyadatech.com)
- Email: info@siyada.tech
- LinkedIn: [Siyada Tech](https://linkedin.com/company/siyada-tech)

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Core LLM integration with Ollama
- [x] Basic web scraping with Firecrawl
- [x] Vector database with Chroma
- [x] Streamlit web interface

### Phase 2 (Q2 2024)
- [ ] Advanced document analysis
- [ ] Multi-language support (Arabic)
- [ ] Integration with legal databases
- [ ] Mobile-responsive interface

### Phase 3 (Q3 2024)
- [ ] Workflow automation
- [ ] Advanced analytics dashboard
- [ ] API for third-party integrations
- [ ] Enterprise deployment options

---

**Made with ❤️ by the DALI team at Siyada Tech**

*Transforming legal practice through innovative AI solutions*

