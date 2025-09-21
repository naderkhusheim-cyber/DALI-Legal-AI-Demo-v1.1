"""
SQL Generator using Ollama for natural language to SQL conversion
"""

import requests
import json
import re
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Generates SQL queries from natural language using Ollama"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Use project configuration or defaults
        if config:
            ollama_config = config.get('ollama', {})
            host = ollama_config.get('host', 'localhost')
            # Handle host with port already included
            if ':' in host:
                self.ollama_host = host.split(':')[0]
                self.ollama_port = int(host.split(':')[1])
            else:
                self.ollama_host = host
                self.ollama_port = ollama_config.get('port', 11435)
            self.model = ollama_config.get('model', 'llama3.2:1b')
        else:
            self.ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
            self.ollama_port = int(os.getenv('OLLAMA_PORT', '11435'))
            self.model = os.getenv('SQL_GENERATION_MODEL', 'llama3.2:1b')
        
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.db_type = "MySQL"
    
    def generate_sql(self, user_query: str, schema_context: str) -> Dict[str, Any]:
        """Generate SQL from natural language query"""
        
        prompt = f"""
You are a SQL expert for a MySQL legal database. Generate ONLY a clean SQL query based on the natural language question.

Database Schema:
{schema_context}

Rules:
1. Only use tables and columns that exist in the schema
2. Use proper MySQL syntax (not SQLite)
3. Use backticks for table and column names if they contain special characters
4. Include appropriate WHERE clauses for legal data filtering
5. Use JOINs when needed to connect related tables
6. Return ONLY the SQL query - NO explanations, comments, or additional text
7. Use proper MySQL date formatting and aggregations
8. Use COALESCE for NULL handling
9. Limit results to 100 rows unless specifically asked for more
10. Use proper MySQL data types and functions
11. End the query with a semicolon
12. Do not include any text after the semicolon

Question: {user_query}

SQL Query:
"""
        
        try:
            response = self._call_ollama(prompt)
            
            if response:
                sql_query = self._clean_sql_query(response)
                
                return {
                    'success': True,
                    'sql_query': sql_query,
                    'original_query': user_query,
                    'model_used': self.model,
                    'db_type': self.db_type
                }
            else:
                # Fallback to OpenAI
                logger.warning("Ollama failed, trying OpenAI fallback")
                return self._fallback_to_openai(prompt, user_query)
                
        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            # Try OpenAI fallback
            try:
                logger.warning("Ollama error, trying OpenAI fallback")
                return self._fallback_to_openai(prompt, user_query)
            except Exception as fallback_error:
                logger.error(f"OpenAI fallback also failed: {fallback_error}")
                return {
                    'success': False,
                    'error': f"Both Ollama and OpenAI failed: {str(e)}"
                }
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API to generate response"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "max_tokens": 512
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Ollama API connection error")
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None
    
    def _clean_sql_query(self, raw_sql: str) -> str:
        """Clean and validate SQL query"""
        
        # Remove markdown formatting
        sql = re.sub(r'```sql\n?', '', raw_sql)
        sql = re.sub(r'```\n?', '', sql)
        
        # Remove explanatory text after semicolon
        if ';' in sql:
            sql = sql.split(';')[0] + ';'
        
        # Remove common explanatory phrases
        explanatory_phrases = [
            r'This query.*?\.',
            r'Note:.*?\.',
            r'Explanation:.*?\.',
            r'Description:.*?\.',
            r'The query.*?\.',
            r'It.*?\.',
            r'This.*?\.',
            r'Note.*?\.'
        ]
        
        for pattern in explanatory_phrases:
            sql = re.sub(pattern, '', sql, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove extra whitespace and newlines
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # Ensure query ends with semicolon
        if not sql.endswith(';'):
            sql += ';'
        
        # Basic MySQL syntax validation
        sql = self._validate_mysql_syntax(sql)
            
        return sql
    
    def _validate_mysql_syntax(self, sql: str) -> str:
        """Basic MySQL syntax validation and correction"""
        
        # Convert common SQLite functions to MySQL equivalents
        sql = re.sub(r'\bLENGTH\b', 'CHAR_LENGTH', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bSUBSTR\b', 'SUBSTRING', sql, flags=re.IGNORECASE)
        
        # Ensure proper LIMIT syntax
        if 'LIMIT' in sql.upper() and not re.search(r'LIMIT\s+\d+', sql, re.IGNORECASE):
            sql = re.sub(r'LIMIT\s*$', 'LIMIT 100', sql, flags=re.IGNORECASE)
        
        return sql
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                logger.info(f"Available models: {model_names}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model.get('name', '') for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    def validate_sql(self, sql_query: str) -> Dict[str, Any]:
        """Validate SQL query syntax (basic validation)"""
        
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for basic SQL structure
        if not sql_query.strip():
            validation_result['valid'] = False
            validation_result['errors'].append('Empty SQL query')
            return validation_result
        
        # Check for SELECT statement
        if not re.search(r'^\s*SELECT\s+', sql_query, re.IGNORECASE):
            validation_result['warnings'].append('Query should start with SELECT')
        
        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', sql_query, re.IGNORECASE):
                validation_result['warnings'].append(f'Query contains {keyword} operation - use with caution')
        
        # Check for proper semicolon
        if not sql_query.rstrip().endswith(';'):
            validation_result['warnings'].append('Query should end with semicolon')
        
        return validation_result

    def _fallback_to_openai(self, prompt: str, user_query: str) -> Dict[str, Any]:
        """Fallback to OpenAI when Ollama fails"""
        try:
            import openai
            import os
            
            # Get OpenAI API key from environment or config
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key not found. Please set OPENAI_API_KEY environment variable.'
                }
            
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert for MySQL databases. Generate ONLY clean SQL queries without explanations."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=512,
                temperature=0.1
            )
            
            sql_query = self._clean_sql_query(response.choices[0].message.content)
            
            return {
                'success': True,
                'sql_query': sql_query,
                'original_query': user_query,
                'model_used': 'gpt-3.5-turbo (fallback)',
                'db_type': self.db_type
            }
            
        except Exception as e:
            logger.error(f"OpenAI fallback error: {e}")
            return {
                'success': False,
                'error': f"OpenAI fallback failed: {str(e)}"
            }

def create_sql_generator(config: Dict[str, Any] = None) -> SQLGenerator:
    """Create a new SQLGenerator instance"""
    return SQLGenerator(config)

# Test function
def test_sql_generator():
    """Test the SQL generator functionality"""
    print("🧪 Testing SQL Generator...")
    
    # Test with sample schema
    sample_schema = """
    Table: clients
      - client_id (int) (PRI) NOT NULL
      - name (varchar(255)) NOT NULL
      - company (varchar(255))
      - contact_email (varchar(255))
      - phone (varchar(50))
      - address (text)
      - client_type (varchar(100))
      - industry (varchar(100))
      - created_date (date)
      - status (varchar(50)) NOT NULL
      - total_value (decimal(15,2))
    
    Table: cases
      - case_id (int) (PRI) NOT NULL
      - case_number (varchar(100)) UNIQUE
      - client_id (int)
      - attorney_id (int)
      - case_type (varchar(100))
      - case_status (varchar(50))
      - filing_date (date)
      - resolution_date (date)
      - case_value (decimal(15,2))
      - outcome (varchar(100))
      - description (text)
    """
    
    generator = SQLGenerator()
    
    # Test connection
    if generator.test_connection():
        print("✅ Ollama connection successful")
        
        # Test SQL generation
        test_queries = [
            "Show me all clients",
            "Find cases with high value",
            "List attorneys by practice area",
            "Show client revenue summary"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            result = generator.generate_sql(query, sample_schema)
            
            if result['success']:
                print(f"✅ Generated SQL: {result['sql_query']}")
                
                # Validate the generated SQL
                validation = generator.validate_sql(result['sql_query'])
                if validation['warnings']:
                    print(f"⚠️  Warnings: {validation['warnings']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        print("\n✅ SQL Generator test completed successfully")
    else:
        print("❌ Failed to connect to Ollama")

if __name__ == "__main__":
    test_sql_generator()
