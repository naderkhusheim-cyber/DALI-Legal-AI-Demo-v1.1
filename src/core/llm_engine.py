"""
DALI Legal AI - LLM Engine Module
Handles interaction with Ollama local language models
"""

import os
import json
import logging
from typing import List, Dict, Optional, Generator
import ollama
import openai
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from src.utils.config import load_config

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses"""
    
    def __init__(self):
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)
        print(token, end="", flush=True)


class LLMEngine:
    """
    Core LLM Engine for DALI Legal AI System
    Manages Ollama models and provides legal-specific prompting
    """
    def __init__(self, model_name: str = None, host: str = None, port: int = None):
        self.config = load_config()
        self.model_name = model_name or self.config.get('ollama', {}).get('model', 'llama3.2:1b')
        self.host = host or self.config.get('ollama', {}).get('host', 'localhost')
        self.port = port or self.config.get('ollama', {}).get('port', 11434)
        self.openai_api_key = self.config.get('openai', {}).get('api_key', None)
        self.openai_model = self.config.get('openai', {}).get('model', 'gpt-4o')
        
        # Handle case where host already contains port
        if ':' in self.host:
            # Extract just the host part if port is included
            self.host = self.host.split(':')[0]
        
        # Initialize Ollama client with error handling
        try:
            self.client = ollama.Client(host=f"http://{self.host}:{self.port}")
            self.ollama_available = True
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama client: {e}")
            self.client = None
            self.ollama_available = False
        
        self.legal_system_prompt = self._get_legal_system_prompt()
        
        # Verify model availability (only for Ollama models and if Ollama is available)
        if self.ollama_available and (self.model_name.startswith('llama') or self.model_name == 'mistral'):
            self._ensure_model_available()
    
    def _extract_model_names(self, list_response: Dict) -> List[str]:
        """Extract model names from ollama list() response safely."""
        try:
            models = list_response
            # Some client versions return {'models': [...]} while others may return a list directly
            if isinstance(models, dict):
                models = models.get('models', [])
            if not isinstance(models, list):
                return []
            names: List[str] = []
            for item in models:
                if isinstance(item, dict):
                    name = item.get('name') or item.get('model')
                    if isinstance(name, str):
                        names.append(name)
                elif isinstance(item, str):
                    names.append(item)
            return names
        except Exception as exc:
            logger.error(f"Failed to parse ollama model list: {exc}")
            return []
    
    def _ensure_model_available(self) -> None:
        """Ensure the specified model is available locally"""
        try:
            models_response = self.client.list()
            available_models = self._extract_model_names(models_response)
            
            if self.model_name not in available_models:
                logger.info(f"Model {self.model_name} not found. Pulling from Ollama...")
                self.client.pull(self.model_name)
                logger.info(f"Successfully pulled {self.model_name}")
                
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            logger.info("Falling back to OpenAI for LLM operations")
            # Don't raise the exception, just log it and continue
    
    def _get_legal_system_prompt(self) -> str:
        """Get the legal-specific system prompt (very explicit about answer language)"""
        return (
            "System Prompt: DALI (Test-Ready)\n\n"
            "Identity / الهوية\n"
            "You are DALI, an AI legal assistant created by Siyada Tech. You assist legal professionals with:\n"
            "أنت دالي، مساعد قانوني ذكي تم تطويره بواسطة شركة سيادة تك. تساعد المتخصصين القانونيين في:\n\n"
            "Research / البحث\n"
            "Document analysis / تحليل المستندات\n"
            "Legal reasoning / الاستدلال القانوني\n\n"
            "Core Rules / القواعد الأساسية\n"
            "Confidentiality / السرية\n"
            "Always treat user inputs as confidential.\n"
            "تعامل دائمًا مع مدخلات المستخدم بسرية تامة.\n\n"
            "Document Context Usage / استخدام سياق المستندات\n"
            "When provided with document context, ALWAYS use it to answer the user's question.\n"
            "If context is provided, base your answer primarily on that information.\n"
            "عند توفير سياق المستندات، استخدمه دائمًا للإجابة على سؤال المستخدم.\n"
            "إذا تم توفير السياق، اعتمد إجابتك بشكل أساسي على تلك المعلومات.\n\n"
            "Separation of Sources / فصل المصادر\n"
            "Always split your output into:\n"
            "قم دائمًا بتقسيم إجابتك إلى:\n"
            "From Knowledge Base → Information found in uploaded documents and user's knowledge base.\n"
            "من قاعدة المعرفة → المعلومات الموجودة في المستندات المرفوعة وقاعدة معرفة المستخدم.\n"
            "Cite the document: / اذكر المستند:\n"
            "From Web → Information from real-time searches.\n"
            "من الويب → المعلومات من عمليات البحث في الوقت الفعلي.\n"
            "Cite with web format: 【web†SourceName†L8-L15】\n"
            "اذكر المصدر بهذا الشكل: 【web†اسم_المصدر†L8-L15】\n\n"
            "Language / اللغة:\n"
            "Always answer in the language of the user's question, regardless of the context or document language.\n"
            "If the question is in English, your answer must be in English, even if the context is in Arabic.\n"
            "If the question is in Arabic, your answer must be in Arabic, even if the context is in English.\n"
            "أجب دائمًا بلغة سؤال المستخدم بغض النظر عن لغة السياق أو المستندات.\n"
            "إذا كان السؤال بالإنجليزية، يجب أن تكون الإجابة بالإنجليزية حتى لو كان السياق أو المستندات بالعربية.\n"
            "إذا كان السؤال بالعربية، يجب أن تكون الإجابة بالعربية حتى لو كان السياق أو المستندات بالإنجليزية.\n"
        )
    
    def generate_response(
        self, 
        query: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> str:
        """
        Generate a response to a legal query
        
        Args:
            query: The user's legal question or request
            context: Additional context from documents or research
            conversation_history: Previous conversation messages
            stream: Whether to stream the response
            
        Returns:
            Generated response string
        """
        try:
            # Build the prompt
            messages = self._build_messages(query, context, conversation_history)
            
            if self.model_name.startswith('gpt'):
                return self._generate_openai_response(query, context)
            elif self.model_name.startswith('llama') or self.model_name == 'mistral':
                return self._generate_ollama_response(query, context)
            else:
                raise ValueError(f"Unsupported model: {self.model_name}. Please select a valid Ollama or OpenAI model.")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    def _build_messages(
        self, 
        query: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Build the message list for the LLM"""
        messages = [{"role": "system", "content": self.legal_system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add context if provided
        user_message = query
        if context:
            user_message = f"Context: {context}\n\nQuestion: {query}"
        
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def _generate_complete_response(self, messages: List[Dict]) -> str:
        """Generate a complete response (non-streaming)"""
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.3,  # Lower temperature for more consistent legal responses
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            )
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error in complete response generation: {e}")
            raise
    
    def _generate_streaming_response(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate a streaming response"""
        try:
            stream = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Error in streaming response generation: {e}")
            yield f"Error: {str(e)}"
    
    def _generate_openai_response(self, query, context=None):
        # Use OpenAI v1+ API
        client = openai.OpenAI(api_key=self.openai_api_key)
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": query})
        response = client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content.strip()

    def _generate_ollama_response(self, query, context=None):
        """Generate a response using an Ollama model."""
        try:
            messages = self._build_messages(query, context)
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=False, # Ensure non-streaming for this method
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error in Ollama response generation: {e}")
            raise

    def analyze_document(self, document_text: str, analysis_type: str = "general") -> str:
        """
        Analyze a legal document
        
        Args:
            document_text: The text content of the document
            analysis_type: Type of analysis (general, contract, litigation, etc.)
            
        Returns:
            Analysis results
        """
        analysis_prompts = {
            "general": "Please analyze this legal document and provide a summary of key points, potential issues, and recommendations.",
            "contract": "Analyze this contract for key terms, obligations, risks, and any unusual or problematic clauses.",
            "litigation": "Review this litigation document and identify key legal arguments, evidence, and strategic considerations.",
            "compliance": "Examine this document for compliance issues and regulatory requirements."
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        full_prompt = f"{prompt}\n\nDocument:\n{document_text}"
        
        return self.generate_response(full_prompt)
    
    def legal_research(self, research_query: str, jurisdiction: str = "Saudi Arabia") -> str:
        """
        Conduct legal research on a specific topic
        
        Args:
            research_query: The legal research question
            jurisdiction: The relevant jurisdiction
            
        Returns:
            Research results and recommendations
        """
        research_prompt = f"""
        Please conduct legal research on the following topic for {jurisdiction}:
        
        {research_query}
        
        Please provide:
        1. Relevant laws and regulations
        2. Key case precedents (if applicable)
        3. Legal principles and interpretations
        4. Practical implications and recommendations
        5. Areas requiring further research or expert consultation
        
        Note: This is for informational purposes and should be verified with current legal sources.
        """
        
        return self.generate_response(research_prompt)
    
    def draft_document(self, document_type: str, requirements: Dict) -> str:
        """
        Draft a legal document based on requirements
        
        Args:
            document_type: Type of document to draft
            requirements: Dictionary of document requirements
            
        Returns:
            Drafted document text
        """
        requirements_text = "\n".join([f"- {k}: {v}" for k, v in requirements.items()])
        
        draft_prompt = f"""
        Please draft a {document_type} with the following requirements:
        
        {requirements_text}
        
        Please ensure the document:
        1. Follows standard legal formatting
        2. Includes all necessary clauses
        3. Uses appropriate legal language
        4. Complies with relevant regulations
        5. Includes placeholders for specific details that need to be filled in
        
        Note: This draft should be reviewed by a qualified attorney before use.
        """
        
        return self.generate_response(draft_prompt)
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        try:
            models_response = self.client.list()
            models = models_response.get('models', models_response) if isinstance(models_response, dict) else models_response
            current_model = None
            if isinstance(models, list):
                for m in models:
                    if isinstance(m, dict) and (m.get('name') == self.model_name or m.get('model') == self.model_name):
                        current_model = m
                        break
            return current_model or {"error": "Model not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if the LLM engine is healthy and responsive"""
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                options={"max_tokens": 10}
            )
            return bool(response.get('message', {}).get('content'))
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    @staticmethod
    def from_user_settings(user_settings, config=None):
        """Create an LLMEngine instance based on user settings (provider/model)."""
        config = config or load_config()
        provider = user_settings.get('llm_provider', 'openai') if user_settings else 'openai'
        model = user_settings.get('llm_model', 'gpt-3.5-turbo') if user_settings else 'gpt-3.5-turbo'
        if provider == 'openai':
            # OpenAI does not need host/port
            return LLMEngine(model_name=model)
        else:
            # Ollama
            host = config.get('ollama', {}).get('host', 'localhost')
            port = config.get('ollama', {}).get('port', 11434)
            return LLMEngine(model_name=model, host=host, port=port)


# Utility functions
def get_available_models(host: str = "localhost", port: int = 11434) -> List[str]:
    """Get list of available Ollama models"""
    try:
        client = ollama.Client(host=f"http://{host}:{port}")
        models_response = client.list()
        # Reuse the robust extractor via a temporary engine instance
        temp_engine = LLMEngine(host=host, port=port)
        return temp_engine._extract_model_names(models_response)
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []


def pull_model(model_name: str, host: str = "localhost", port: int = 11434) -> bool:
    """Pull a model from Ollama registry"""
    try:
        client = ollama.Client(host=f"http://{host}:{port}")
        client.pull(model_name)
        return True
    except Exception as e:
        logger.error(f"Error pulling model {model_name}: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    engine = LLMEngine()
    
    # Test basic functionality
    if engine.health_check():
        print("✅ LLM Engine is healthy")
        
        # Test legal research
        research_result = engine.legal_research(
            "What are the requirements for forming a limited liability company in Saudi Arabia?"
        )
        print(f"Research Result: {research_result[:200]}...")
        
    else:
        print("❌ LLM Engine health check failed")

