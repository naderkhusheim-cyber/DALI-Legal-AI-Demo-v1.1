#!/bin/bash

# DALI Legal AI MVP - Setup Script
# Development of Ambitious Leading Ideas @ Siyada Tech

echo "🚀 Setting up DALI Legal AI MVP..."
echo "Development of Ambitious Leading Ideas @ Siyada Tech"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install Ollama
echo "📦 Installing Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed: $(ollama --version)"
else
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Failed to install Ollama. Please install manually."
        exit 1
    fi
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv dali_env
source dali_env/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully!"
else
    echo "❌ Failed to install Python dependencies."
    exit 1
fi

# Download Ollama models
echo "🤖 Downloading Ollama models..."
echo "This may take a few minutes depending on your internet connection..."

# Start Ollama service in background
ollama serve &
OLLAMA_PID=$!
sleep 5  # Wait for Ollama to start

# Download essential models
echo "Downloading Llama 3 (4GB)..."
ollama pull llama3

echo "Downloading Nomic Embed Text (for embeddings)..."
ollama pull nomic-embed-text

echo "Downloading Mistral (optional, 4GB)..."
ollama pull mistral

# Kill background Ollama process
kill $OLLAMA_PID 2>/dev/null

# Create .env file template
echo "📝 Creating environment configuration..."
cat > .env << EOF
# DALI Legal AI MVP Configuration
# Development of Ambitious Leading Ideas @ Siyada Tech

# Firecrawl API Configuration
# Get your API key from: https://firecrawl.dev
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./dali_vectordb

# Application Configuration
DEFAULT_MODEL=llama3
MAX_DOCUMENTS=1000
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start_dali.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting DALI Legal AI MVP..."
echo "Development of Ambitious Leading Ideas @ Siyada Tech"

# Activate virtual environment
source dali_env/bin/activate

# Start Ollama service
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 3

# Start Streamlit app
echo "Starting DALI Legal AI web interface..."
echo "Open your browser to: http://localhost:8501"
streamlit run dali_streamlit_app.py

# Cleanup on exit
trap "kill $OLLAMA_PID 2>/dev/null" EXIT
EOF

chmod +x start_dali.sh

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p dali_vectordb
mkdir -p logs
mkdir -p data/scraped
mkdir -p data/uploads

echo ""
echo "🎉 DALI Legal AI MVP setup complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file and add your Firecrawl API key"
echo "2. Run: ./start_dali.sh"
echo "3. Open your browser to: http://localhost:8501"
echo ""
echo "🔧 Manual Commands:"
echo "• Start Ollama: ollama serve"
echo "• Start Web Interface: streamlit run dali_streamlit_app.py"
echo "• Test System: python dali_technical_implementation.py"
echo ""
echo "📚 Documentation:"
echo "• Ollama: https://ollama.ai/docs"
echo "• Firecrawl: https://firecrawl.dev/docs"
echo "• Streamlit: https://docs.streamlit.io"
echo ""
echo "🚀 DALI - Where ambitious legal ideas become reality!"
echo "Contact: dali@siyada.tech"

