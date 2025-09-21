#!/bin/bash

# DALI Legal AI System Start Script
# Starts all necessary services and the web interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="dali-env"
STREAMLIT_PORT=8501
OLLAMA_MODEL="llama3.2:1b"

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

# Function to check if port is available
is_port_available() {
    ! lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval "$check_command" >/dev/null 2>&1; then
            print_success "$service_name is ready"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_status "Still waiting for $service_name... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to start Ollama service
start_ollama() {
    print_status "Starting Ollama service..."
    
    if ! command_exists ollama; then
        print_error "Ollama not found. Please run setup.sh first."
        return 1
    fi
    
    # Check if Ollama is already running
    if ollama list >/dev/null 2>&1; then
        print_success "Ollama is already running"
        return 0
    fi
    
    # Start Ollama service
    if command_exists systemctl; then
        # Try systemd service first
        if sudo systemctl start ollama 2>/dev/null; then
            print_success "Ollama service started via systemd"
        else
            print_warning "Could not start Ollama via systemd, trying manual start..."
            # Start Ollama manually in background
            nohup ollama serve > logs/ollama.log 2>&1 &
            echo $! > logs/ollama.pid
        fi
    else
        # Start Ollama manually
        print_status "Starting Ollama manually..."
        nohup ollama serve > logs/ollama.log 2>&1 &
        echo $! > logs/ollama.pid
    fi
    
    # Wait for Ollama to be ready
    if wait_for_service "Ollama" "ollama list"; then
        return 0
    else
        return 1
    fi
}

# Function to check Ollama model
check_ollama_model() {
    print_status "Checking Ollama model: $OLLAMA_MODEL"
    
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL is available"
        return 0
    else
        print_warning "Model $OLLAMA_MODEL not found"
        print_status "Pulling model $OLLAMA_MODEL (this may take a while)..."
        
        if ollama pull "$OLLAMA_MODEL"; then
            print_success "Model $OLLAMA_MODEL pulled successfully"
            return 0
        else
            print_error "Failed to pull model $OLLAMA_MODEL"
            return 1
        fi
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment: $VENV_NAME"
    
    if [ ! -d "$VENV_NAME" ]; then
        print_error "Virtual environment $VENV_NAME not found. Please run setup.sh first."
        return 1
    fi
    
    source "$VENV_NAME/bin/activate"
    print_success "Virtual environment activated"
    return 0
}

# Function to check Python dependencies
check_dependencies() {
    print_status "Checking Python dependencies..."
    
    python3 -c "
import sys
sys.path.append('src')

required_modules = [
    'streamlit',
    'ollama',
    'chromadb',
    'sentence_transformers',
    'langchain'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'Missing modules: {missing_modules}')
    sys.exit(1)
else:
    print('All required modules are available')
"
    
    if [ $? -eq 0 ]; then
        print_success "All Python dependencies are available"
        return 0
    else
        print_error "Missing Python dependencies. Please run setup.sh first."
        return 1
    fi
}

# Function to start Streamlit application
start_streamlit() {
    print_status "Starting DALI Legal AI web interface..."
    
    # Check if port is available
    if ! is_port_available $STREAMLIT_PORT; then
        print_error "Port $STREAMLIT_PORT is already in use"
        print_status "Please stop the service using that port or change STREAMLIT_PORT in the configuration"
        return 1
    fi
    
    # Set Streamlit configuration
    export STREAMLIT_SERVER_PORT=$STREAMLIT_PORT
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    
    # Start Streamlit
    print_status "Starting web interface on port $STREAMLIT_PORT..."
    streamlit run src/web/app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0
}

# Function to perform health checks
health_check() {
    print_status "Performing health checks..."
    
    local all_healthy=true
    
    # Check Ollama
    if ollama list >/dev/null 2>&1; then
        print_success "✅ Ollama service is healthy"
    else
        print_error "❌ Ollama service is not responding"
        all_healthy=false
    fi
    
    # Check model availability
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "✅ Model $OLLAMA_MODEL is available"
    else
        print_warning "⚠️ Model $OLLAMA_MODEL is not available"
        all_healthy=false
    fi
    
    # Check Python environment
    if python3 -c "import streamlit, ollama, chromadb" 2>/dev/null; then
        print_success "✅ Python environment is healthy"
    else
        print_error "❌ Python environment has issues"
        all_healthy=false
    fi
    
    # Check data directories
    if [ -d "data/embeddings" ] && [ -d "logs" ]; then
        print_success "✅ Data directories exist"
    else
        print_warning "⚠️ Some data directories are missing"
        mkdir -p data/embeddings logs
    fi
    
    if $all_healthy; then
        print_success "All health checks passed"
        return 0
    else
        print_warning "Some health checks failed - the system may not work correctly"
        return 1
    fi
}

# Function to show startup information
show_startup_info() {
    echo
    echo "=========================================="
    echo -e "${GREEN}🚀 DALI Legal AI Starting Up 🚀${NC}"
    echo "=========================================="
    echo
    echo "System Information:"
    echo "- Ollama Model: $OLLAMA_MODEL"
    echo "- Web Interface Port: $STREAMLIT_PORT"
    echo "- Virtual Environment: $VENV_NAME"
    echo
    echo "Access the application at:"
    echo -e "  ${BLUE}http://localhost:$STREAMLIT_PORT${NC}"
    echo
    echo "Press Ctrl+C to stop the application"
    echo
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down DALI Legal AI..."
    
    # Kill Ollama if we started it manually
    if [ -f "logs/ollama.pid" ]; then
        local ollama_pid=$(cat logs/ollama.pid)
        if kill -0 "$ollama_pid" 2>/dev/null; then
            print_status "Stopping Ollama service (PID: $ollama_pid)"
            kill "$ollama_pid"
            rm -f logs/ollama.pid
        fi
    fi
    
    print_success "DALI Legal AI stopped"
    exit 0
}

# Main function
main() {
    # Handle interruption
    trap cleanup INT TERM
    
    # Show startup information
    show_startup_info
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Step 1: Activate virtual environment
    if ! activate_venv; then
        exit 1
    fi
    
    # Step 2: Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Step 3: Start Ollama service
    if ! start_ollama; then
        print_error "Failed to start Ollama service"
        exit 1
    fi
    
    # Step 4: Check Ollama model
    if ! check_ollama_model; then
        print_warning "Ollama model check failed - some features may not work"
    fi
    
    # Step 5: Perform health checks
    health_check
    
    echo
    print_success "All services started successfully!"
    echo
    print_status "Starting web interface..."
    echo
    
    # Step 6: Start Streamlit application
    start_streamlit
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

