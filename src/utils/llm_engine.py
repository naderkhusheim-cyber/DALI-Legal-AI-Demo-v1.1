"""
LLM Engine for DALI Legal AI System
Provides unified interface for different LLM providers (OpenAI, Ollama, etc.)
"""

import logging
from typing import Dict, Any, Optional
from src.utils.config import load_config

logger = logging.getLogger(__name__)

class LLMEngine:
    """Unified LLM engine for different providers"""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo", **kwargs):
        self.provider = provider
        self.model = model
        self.config = load_config()
        self.kwargs = kwargs
        
    @classmethod
    def from_user_settings(cls, settings: Dict[str, Any]) -> 'LLMEngine':
        """Create LLM engine from user settings"""
        provider = settings.get('llm_provider', 'openai')
        model = settings.get('llm_model', 'gpt-3.5-turbo')
        return cls(provider=provider, model=model, **settings)
    
    def analyze_document(self, document_text: str, analysis_type: str) -> str:
        """Analyze document using the configured LLM"""
        try:
            if self.provider == "openai":
                return self._analyze_with_openai(document_text, analysis_type)
            elif self.provider == "ollama":
                return self._analyze_with_ollama(document_text, analysis_type)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise
    
    def _analyze_with_openai(self, document_text: str, analysis_type: str) -> str:
        """Analyze document using OpenAI"""
        try:
            import openai
            
            # Get OpenAI configuration
            openai_config = self.config.get('openai', {})
            api_key = openai_config.get('api_key')
            model = openai_config.get('model', 'gpt-3.5-turbo')
            temperature = openai_config.get('temperature', 0.3)
            max_tokens = openai_config.get('max_tokens', 2048)
            
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Set up OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Create analysis prompt based on type
            prompt = self._create_analysis_prompt(document_text, analysis_type)
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal AI assistant specializing in document analysis. Provide comprehensive, accurate, and professional analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            raise
    
    def _analyze_with_ollama(self, document_text: str, analysis_type: str) -> str:
        """Analyze document using Ollama (fallback)"""
        try:
            import requests
            
            # Get Ollama configuration
            ollama_config = self.config.get('ollama', {})
            host = ollama_config.get('host', '127.0.0.1')
            port = ollama_config.get('port', 11435)
            model = ollama_config.get('model', 'llama3.2:1b')
            
            # Handle case where host already includes port
            if ':' in host:
                url = f"http://{host}/api/generate"
            else:
                url = f"http://{host}:{port}/api/generate"
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(document_text, analysis_type)
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from Ollama')
            
        except Exception as e:
            logger.error(f"Ollama analysis failed: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, document_text: str, analysis_type: str) -> str:
        """Create analysis prompt based on type"""
        
        prompts = {
            "summary": f"""
Please provide a comprehensive summary of the following legal document:

Document Text:
{document_text}

Please include:
1. Document overview and main purpose
2. Key parties involved
3. Main legal issues or topics
4. Important dates and deadlines
5. Key findings or conclusions
6. Recommendations or next steps

Format your response in clear, professional language suitable for legal professionals.
""",
            
            "contract": f"""
Please analyze the following document as a legal contract:

Document Text:
{document_text}

Please provide:
1. Contract type and nature
2. Parties involved and their roles
3. Key terms and conditions
4. Obligations and responsibilities
5. Payment terms (if applicable)
6. Duration and termination clauses
7. Risk factors and potential issues
8. Compliance requirements
9. Recommendations for review or modification

Focus on identifying potential legal risks and areas that may need attention.
""",
            
            "litigation": f"""
Please analyze the following document for litigation purposes:

Document Text:
{document_text}

Please provide:
1. Case overview and legal issues
2. Parties and their positions
3. Factual background
4. Legal arguments and claims
5. Evidence and supporting materials
6. Procedural history
7. Potential legal remedies
8. Strengths and weaknesses of each party's position
9. Settlement considerations
10. Strategic recommendations

Focus on litigation strategy and case assessment.
""",
            
            "compliance": f"""
Please analyze the following document for compliance purposes:

Document Text:
{document_text}

Please provide:
1. Applicable laws and regulations
2. Compliance requirements
3. Risk assessment
4. Regulatory obligations
5. Documentation requirements
6. Monitoring and reporting needs
7. Potential violations or issues
8. Corrective actions needed
9. Best practices recommendations
10. Ongoing compliance considerations

Focus on regulatory compliance and risk management.
"""
        }
        
        return prompts.get(analysis_type, prompts["summary"])
    
    def generate_response(self, query: str, context: str = "") -> str:
        """Generate response to a query with optional context"""
        try:
            if self.provider == "openai":
                return self._generate_with_openai(query, context)
            elif self.provider == "ollama":
                return self._generate_with_ollama(query, context)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise
    
    def _generate_with_openai(self, query: str, context: str = "") -> str:
        """Generate response using OpenAI"""
        try:
            import openai
            
            openai_config = self.config.get('openai', {})
            api_key = openai_config.get('api_key')
            model = openai_config.get('model', 'gpt-3.5-turbo')
            temperature = openai_config.get('temperature', 0.3)
            max_tokens = openai_config.get('max_tokens', 2048)
            
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = openai.OpenAI(api_key=api_key)
            
            messages = [
                {"role": "system", "content": "You are a legal AI assistant. Provide accurate, helpful, and professional legal information."}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": query})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI response generation failed: {str(e)}")
            raise
    
    def _generate_with_ollama(self, query: str, context: str = "") -> str:
        """Generate response using Ollama"""
        try:
            import requests
            
            ollama_config = self.config.get('ollama', {})
            host = ollama_config.get('host', '127.0.0.1')
            port = ollama_config.get('port', 11435)
            model = ollama_config.get('model', 'llama3.2:1b')
            
            # Handle case where host already includes port
            if ':' in host:
                url = f"http://{host}/api/generate"
            else:
                url = f"http://{host}:{port}/api/generate"
            
            prompt = f"You are a legal AI assistant. Provide accurate, helpful, and professional legal information.\n\n"
            if context:
                prompt += f"Context: {context}\n\n"
            prompt += f"Query: {query}"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from Ollama')
            
        except Exception as e:
            logger.error(f"Ollama response generation failed: {str(e)}")
            raise
