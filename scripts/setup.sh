#!/bin/bash

# DALI Legal AI System Setup Script
# Automated installation and configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
OLLAMA_MODEL="llama3"
VENV_NAME="dali-env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION=$PYTHON_MIN_VERSION
        
        if python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$REQUIRED_VERSION'.split('.'))) else 1)"; then
            print_success "Python $PYTHON_VERSION found (>= $PYTHON_MIN_VERSION required)"
            return 0
        else
            print_error "Python $PYTHON_VERSION found, but >= $PYTHON_MIN_VERSION required"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.$PYTHON_MIN_VERSION or higher"
        return 1
    fi
}

# Function to install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    if command_exists ollama; then
        print_success "Ollama already installed"
        return 0
    fi
    
    # Install Ollama
    if curl -fsSL https://ollama.com/install.sh | sh; then
        print_success "Ollama installed successfully"
        
        # Start Ollama service
        print_status "Starting Ollama service..."
        if command_exists systemctl; then
            sudo systemctl start ollama || print_warning "Could not start Ollama service automatically"
        fi
        
        return 0
    else
        print_error "Failed to install Ollama"
        return 1
    fi
}

# Function to pull Ollama model
pull_ollama_model() {
    print_status "Pulling Ollama model: $OLLAMA_MODEL"
    
    # Wait for Ollama to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ollama list >/dev/null 2>&1; then
            break
        fi
        print_status "Waiting for Ollama to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Ollama service not responding after $max_attempts attempts"
        return 1
    fi
    
    # Check if model already exists
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL already available"
        return 0
    fi
    
    # Pull the model
    if ollama pull "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL pulled successfully"
        return 0
    else
        print_error "Failed to pull model $OLLAMA_MODEL"
        return 1
    fi
}

# Function to create Python virtual environment
create_virtual_env() {
    print_status "Creating Python virtual environment: $VENV_NAME"
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment $VENV_NAME already exists"
        return 0
    fi
    
    if python3 -m venv "$VENV_NAME"; then
        print_success "Virtual environment created: $VENV_NAME"
        return 0
    else
        print_error "Failed to create virtual environment"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if pip install -r requirements.txt; then
        print_success "Python dependencies installed successfully"
        return 0
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    local dirs=(
        "data/documents"
        "data/embeddings"
        "logs"
        "config"
    )
    
    for dir in "${dirs[@]}"; do
        if mkdir -p "$dir"; then
            print_success "Created directory: $dir"
        else
            print_error "Failed to create directory: $dir"
            return 1
        fi
    done
    
    return 0
}

# Function to create configuration file
create_config() {
    print_status "Creating configuration file..."
    
    if [ ! -f "config/config.yaml" ]; then
        python3 -c "
import sys
sys.path.append('src')
from utils.config import create_sample_config
create_sample_config('config/config.yaml')
"
        if [ $? -eq 0 ]; then
            print_success "Configuration file created: config/config.yaml"
        else
            print_error "Failed to create configuration file"
            return 1
        fi
    else
        print_warning "Configuration file already exists: config/config.yaml"
    fi
    
    return 0
}

# Function to create .env file
create_env_file() {
    print_status "Creating environment file..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# DALI Legal AI Environment Configuration

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=$OLLAMA_MODEL

# Firecrawl Configuration (optional)
# FIRECRAWL_API_KEY=your_api_key_here

# Chroma Configuration
CHROMA_PERSIST_DIRECTORY=./data/embeddings
CHROMA_COLLECTION_NAME=legal_documents

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0

# Security (generate your own keys in production)
# DALI_SECRET_KEY=your_secret_key_here
# DALI_ENCRYPTION_KEY=your_encryption_key_here
EOF
        print_success "Environment file created: .env"
    else
        print_warning "Environment file already exists: .env"
    fi
    
    return 0
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Test Python imports
    python3 -c "
import sys
sys.path.append('src')

try:
    from core.llm_engine import LLMEngine
    from core.vector_store import VectorStore
    from scrapers.firecrawl_scraper import FirecrawlScraper
    from utils.config import get_config
    print('✅ All Python modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Python modules test passed"
    else
        print_error "Python modules test failed"
        return 1
    fi
    
    # Test Ollama connection
    if ollama list >/dev/null 2>&1; then
        print_success "Ollama connection test passed"
    else
        print_warning "Ollama connection test failed - service may not be running"
    fi
    
    return 0
}

# Function to display completion message
show_completion_message() {
    echo
    echo "=========================================="
    echo -e "${GREEN}🎉 DALI Legal AI Setup Complete! 🎉${NC}"
    echo "=========================================="
    echo
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo -e "   ${BLUE}source $VENV_NAME/bin/activate${NC}"
    echo
    echo "2. Start the application:"
    echo -e "   ${BLUE}streamlit run src/web/app.py${NC}"
    echo
    echo "3. Open your browser to:"
    echo -e "   ${BLUE}http://localhost:8501${NC}"
    echo
    echo "Configuration files:"
    echo "- Main config: config/config.yaml"
    echo "- Environment: .env"
    echo
    echo "For help and documentation:"
    echo "- README.md"
    echo "- docs/ directory"
    echo
    echo "Happy legal AI research! ⚖️"
    echo
}

# Main installation function
main() {
    echo "=========================================="
    echo -e "${BLUE}🚀 DALI Legal AI Setup Script 🚀${NC}"
    echo "=========================================="
    echo
    echo "This script will install and configure the DALI Legal AI system."
    echo "Please ensure you have sudo privileges for system-level installations."
    echo
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Setup cancelled by user"
            exit 0
        fi
    fi
    
    # System checks
    print_status "Performing system checks..."
    
    # Check Python version
    if ! check_python_version; then
        print_error "Python version check failed"
        exit 1
    fi
    
    # Check for required system tools
    local required_tools=("curl" "git")
    for tool in "${required_tools[@]}"; do
        if ! command_exists "$tool"; then
            print_error "Required tool not found: $tool"
            print_status "Please install $tool and run this script again"
            exit 1
        fi
    done
    
    print_success "System checks passed"
    echo
    
    # Installation steps
    print_status "Starting installation process..."
    echo
    
    # Step 1: Install Ollama
    if ! install_ollama; then
        print_error "Ollama installation failed"
        exit 1
    fi
    echo
    
    # Step 2: Create directories
    if ! create_directories; then
        print_error "Directory creation failed"
        exit 1
    fi
    echo
    
    # Step 3: Create virtual environment
    if ! create_virtual_env; then
        print_error "Virtual environment creation failed"
        exit 1
    fi
    echo
    
    # Step 4: Install Python dependencies
    if ! install_python_deps; then
        print_error "Python dependencies installation failed"
        exit 1
    fi
    echo
    
    # Step 5: Pull Ollama model
    if ! pull_ollama_model; then
        print_warning "Ollama model pull failed - you can try again later with: ollama pull $OLLAMA_MODEL"
    fi
    echo
    
    # Step 6: Create configuration files
    if ! create_config; then
        print_error "Configuration creation failed"
        exit 1
    fi
    
    if ! create_env_file; then
        print_error "Environment file creation failed"
        exit 1
    fi
    echo
    
    # Step 7: Test installation
    if ! test_installation; then
        print_warning "Installation tests failed - some components may not work correctly"
    fi
    echo
    
    # Show completion message
    show_completion_message
}

# Handle script interruption
trap 'print_error "Setup interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"

