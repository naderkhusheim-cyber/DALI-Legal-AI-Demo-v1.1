"""
DALI Legal AI - Configuration Management
Handles system configuration and environment variables
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for DALI Legal AI System"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/config.yaml"
        self.config_data = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file and environment variables"""
        try:
            # Load from YAML file if it exists
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as file:
                    self.config_data = yaml.safe_load(file) or {}
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.info(f"Configuration file {config_path} not found, using defaults")
                self.config_data = self.get_default_config()
            # DEBUG: Print config after file load
            print("DEBUG: Loaded config from", self.config_file)
            print("DEBUG: firecrawl section after file load:", self.config_data.get('firecrawl'))
            # Override with environment variables
            self._load_env_overrides()
            # DEBUG: Print config after env override
            print("DEBUG: firecrawl section after env override:", self.config_data.get('firecrawl'))
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config_data = self.get_default_config()
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables"""
        env_mappings = {
            # Ollama settings
            'OLLAMA_HOST': ['ollama', 'host'],
            'OLLAMA_PORT': ['ollama', 'port'],
            'OLLAMA_MODEL': ['ollama', 'model'],
            
            # Firecrawl settings
            'FIRECRAWL_API_KEY': ['firecrawl', 'api_key'],
            
            # Chroma settings
            'CHROMA_PERSIST_DIRECTORY': ['chroma', 'persist_directory'],
            'CHROMA_COLLECTION_NAME': ['chroma', 'collection_name'],
            
            # Streamlit settings
            'STREAMLIT_PORT': ['streamlit', 'port'],
            'STREAMLIT_HOST': ['streamlit', 'host'],
            
            # Security settings
            'DALI_SECRET_KEY': ['security', 'secret_key'],
            'DALI_ENCRYPTION_KEY': ['security', 'encryption_key'],
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_config(config_path, env_value)
    
    def _set_nested_config(self, path: list, value: Any) -> None:
        """Set nested configuration value"""
        current = self.config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        
        current[path[-1]] = value
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'ollama': {
                'host': 'localhost',
                'port': 11434,
                'model': 'llama3.2:1b',
                'temperature': 0.3,
                'max_tokens': 2048
            },
            'chroma': {
                'persist_directory': './data/embeddings',
                'collection_name': 'legal_documents',
                'embedding_model': 'all-MiniLM-L6-v2'
            },
            'firecrawl': {
                'api_key': None,
                'timeout': 30000,
                'wait_for': 3000
            },
            'streamlit': {
                'host': '0.0.0.0',
                'port': 8501,
                'theme': 'light'
            },
            'document_processing': {
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'max_file_size_mb': 50
            },
            'security': {
                'secret_key': None,
                'encryption_key': None,
                'session_timeout': 3600
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/dali.log'
            },
            'features': {
                'web_scraping': True,
                'document_upload': True,
                'knowledge_base': True,
                'conversation_history': True
            },
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'ap-hoHfB;6da',
                'database': 'dali_legal_ai'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            current = self.config_data
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
        except Exception as e:
            logger.error(f"Error setting configuration {key}: {e}")
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        try:
            save_path = Path(file_path or self.config_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config_data, file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required settings
        required_settings = [
            ('ollama.host', str),
            ('ollama.port', int),
            ('ollama.model', str),
            ('chroma.persist_directory', str),
            ('chroma.collection_name', str)
        ]
        
        for setting, expected_type in required_settings:
            value = self.get(setting)
            if value is None:
                validation_results['errors'].append(f"Missing required setting: {setting}")
                validation_results['valid'] = False
            elif not isinstance(value, expected_type):
                validation_results['errors'].append(
                    f"Invalid type for {setting}: expected {expected_type.__name__}, got {type(value).__name__}"
                )
                validation_results['valid'] = False
        
        # Check optional but recommended settings
        recommended_settings = [
            'firecrawl.api_key',
            'security.secret_key'
        ]
        
        for setting in recommended_settings:
            if self.get(setting) is None:
                validation_results['warnings'].append(f"Recommended setting not configured: {setting}")
        
        # Validate file paths
        persist_dir = self.get('chroma.persist_directory')
        if persist_dir:
            try:
                Path(persist_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                validation_results['errors'].append(f"Cannot create persist directory: {e}")
                validation_results['valid'] = False
        
        return validation_results
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama-specific configuration"""
        return self.get('ollama', {})
    
    def get_chroma_config(self) -> Dict[str, Any]:
        """Get Chroma-specific configuration"""
        return self.get('chroma', {})
    
    def get_firecrawl_config(self) -> Dict[str, Any]:
        """Get Firecrawl-specific configuration"""
        return self.get('firecrawl', {})
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit-specific configuration"""
        return self.get('streamlit', {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f'features.{feature}', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.config_data.copy()
    
    def to_json(self) -> str:
        """Get configuration as JSON string"""
        return json.dumps(self.config_data, indent=2)


# Global configuration instance
_config_instance = None


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load and return configuration"""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_file)
    
    return _config_instance.to_dict()


def get_config() -> Config:
    """Get configuration instance"""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config()
    
    return _config_instance


def setup_logging(config: Optional[Dict] = None) -> None:
    """Setup logging based on configuration"""
    if config is None:
        config = get_config().get('logging', {})
    
    log_level = getattr(logging, config.get('level', 'INFO').upper())
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('file')
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def create_sample_config(output_path: str = "config/config.yaml") -> bool:
    """Create a sample configuration file"""
    try:
        config = Config()
        sample_config = config.get_default_config()
        
        # Add comments to the sample config
        sample_yaml = """# DALI Legal AI System Configuration
# This file contains all configuration options for the DALI Legal AI system

# Ollama LLM Engine Configuration
ollama:
  host: 127.0.0.1 # Ollama server host
  port: 11435            # Ollama server port
  model: llama3.2:1b          # Default model to use (llama3, mistral, codellama)
  temperature: 0.3        # Response temperature (0.0-1.0)
  max_tokens: 2048        # Maximum response tokens

# Chroma Vector Database Configuration
chroma:
  persist_directory: ./data/embeddings    # Directory to store embeddings
  collection_name: legal_documents        # Collection name for documents
  embedding_model: all-MiniLM-L6-v2     # Sentence transformer model

# Firecrawl Web Scraping Configuration
firecrawl:
  api_key: null           # Firecrawl API key (optional)
  timeout: 30000          # Request timeout in milliseconds
  wait_for: 3000          # Page load wait time in milliseconds

# Streamlit Web Interface Configuration
streamlit:
  host: 0.0.0.0          # Interface host (0.0.0.0 for all interfaces)
  port: 8501             # Interface port
  theme: light           # UI theme (light/dark)

# Document Processing Configuration
document_processing:
  chunk_size: 1000       # Text chunk size for processing
  chunk_overlap: 200     # Overlap between chunks
  max_file_size_mb: 50   # Maximum file size for upload

# Security Configuration
security:
  secret_key: null       # Secret key for encryption (generate one)
  encryption_key: null   # Encryption key for sensitive data
  session_timeout: 3600  # Session timeout in seconds

# Logging Configuration
logging:
  level: INFO            # Log level (DEBUG, INFO, WARNING, ERROR)
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: logs/dali.log    # Log file path

# Feature Flags
features:
  web_scraping: true           # Enable web scraping functionality
  document_upload: true        # Enable document upload
  knowledge_base: true         # Enable knowledge base features
  conversation_history: true   # Enable conversation history
"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(sample_yaml)
        
        logger.info(f"Sample configuration created at {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample configuration: {e}")
        return False


def get_mysql_config():
    config = load_config()
    mysql_cfg = config.get('mysql', {})
    return {
        'host': mysql_cfg.get('host', 'localhost'),
        'port': mysql_cfg.get('port', 3306),
        'user': mysql_cfg.get('user', 'dali_user'),
        'password': mysql_cfg.get('password', 'ap-hoHfB;6da'),
        'database': mysql_cfg.get('database', 'dali_legal_ai')
    }


if __name__ == "__main__":
    # Example usage
    config = get_config()
    
    print("Configuration loaded:")
    print(config.to_json())
    
    # Validate configuration
    validation = config.validate_config()
    print(f"\nValidation results: {validation}")
    
    # Create sample config
    create_sample_config("sample_config.yaml")

