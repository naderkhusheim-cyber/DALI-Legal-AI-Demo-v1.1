"""
FastAPI routes for Enhanced Knowledge Base functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from src.core.database.manager import DatabaseManager
from src.core.database.sql_generator import SQLGenerator
from src.core.database.chart_generator import ChartGenerator
from src.utils.config import load_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])

# Pydantic models
class DatabaseConnection(BaseModel):
    db_type: str
    db_path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class SQLQuery(BaseModel):
    query: str
    natural_language: str

class NaturalLanguageQuery(BaseModel):
    natural_language: str

# Global instances - initialized with project configuration
config = load_config('config/config.yaml')
db_manager = DatabaseManager(config)
sql_generator = SQLGenerator(config)
chart_generator = ChartGenerator(config)

@router.post("/connect")
async def connect_database(connection: DatabaseConnection):
    """Connect to a database"""
    
    try:
        if connection.db_type.lower() == "mysql":
            # Use MySQL connection from project config
            mysql_config = config.get('mysql', {})
            success = db_manager.connect_mysql(
                host=connection.host or mysql_config.get('host', 'localhost'),
                port=connection.port or mysql_config.get('port', 3306),
                database=connection.database or mysql_config.get('database', 'dali_legal_ai'),
                username=connection.username or mysql_config.get('user', 'dali_user'),
                password=connection.password or mysql_config.get('password', 'dali_password')
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Connected to MySQL database: {connection.database or mysql_config.get('database')}",
                    "connection_info": db_manager.get_connection_info()
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to connect to MySQL database")
        
        elif connection.db_type.lower() == "sqlite":
            # SQLite support not implemented in current DatabaseManager
            # Return a message indicating this limitation
            return {
                "success": False, 
                "message": "SQLite support not implemented. Please use MySQL database.",
                "suggestion": "Use db_type: 'mysql' to connect to the MySQL database"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Database type '{connection.db_type}' not supported")
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema")
async def get_database_schema():
    """Get database schema information"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        schema = db_manager.get_schema()
        return {
            "success": True,
            "schema": schema,
            "connection_info": db_manager.get_connection_info()
        }
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-sql")
async def generate_sql(query_request: NaturalLanguageQuery):
    """Generate SQL from natural language"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        schema_context = db_manager.get_schema_context()
        result = sql_generator.generate_sql(query_request.natural_language, schema_context)
        
        if result['success']:
            return {
                "success": True,
                "sql_query": result['sql_query'],
                "natural_language": query_request.natural_language,
                "model_used": result.get('model_used', 'unknown'),
                "reasoning": result.get('reasoning', 'SQL generated successfully')
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-query")
async def execute_query(query_request: SQLQuery):
    """Execute SQL query and return results"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        success, result = db_manager.execute_query(query_request.query)
        
        if success:
            if hasattr(result, 'to_dict'):
                data = result.to_dict(orient='records')
                columns = list(result.columns)
            else:
                data = result
                columns = list(result[0].keys()) if result and isinstance(result[0], dict) else []
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data),
                "executed_query": query_request.query
            }
        else:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {result}")
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-chart")
async def generate_chart(query_request: SQLQuery):
    """Generate chart from query results"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        success, df = db_manager.execute_query(query_request.query)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {df}")
        
        chart_result = chart_generator.generate_chart(df, query_request.natural_language)
        
        if chart_result['success']:
            return {
                "success": True,
                "chart_html": chart_result['chart_html'],
                "chart_config": chart_result['chart_config'],
                "reasoning": chart_result['reasoning'],
                "data_points": len(df)
            }
        else:
            raise HTTPException(status_code=400, detail=chart_result['error'])
            
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/natural-language-query")
async def natural_language_query(query_request: NaturalLanguageQuery):
    """Complete natural language to visualization pipeline"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        # Step 1: Generate SQL
        schema_context = db_manager.get_schema_context()
        sql_result = sql_generator.generate_sql(query_request.natural_language, schema_context)
        
        if not sql_result['success']:
            raise HTTPException(status_code=400, detail=f"SQL generation failed: {sql_result['error']}")
        
        # Step 2: Execute SQL
        success, df = db_manager.execute_query(sql_result['sql_query'])
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {df}")
        
        # Step 3: Generate Chart
        chart_result = chart_generator.generate_chart(df, query_request.natural_language)
        
        if not chart_result['success']:
            raise HTTPException(status_code=400, detail=f"Chart generation failed: {chart_result['error']}")
        
        # Prepare data for response
        if hasattr(df, 'to_dict'):
            data = df.to_dict(orient='records')
            columns = list(df.columns)
        else:
            data = df
            columns = list(df[0].keys()) if df and isinstance(df[0], dict) else []
        
        return {
            "success": True,
            "natural_language": query_request.natural_language,
            "sql_query": sql_result['sql_query'],
            "data": data,
            "columns": columns,
            "row_count": len(data),
            "chart_html": chart_result['chart_html'],
            "chart_config": chart_result['chart_config'],
            "reasoning": chart_result['reasoning'],
            "model_used": sql_result.get('model_used', 'unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Natural language query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-queries")
async def get_sample_queries():
    """Get sample legal database queries"""
    
    sample_queries = [
        {
            "question": "Show me all clients with total value over $200,000",
            "category": "Client Management",
            "description": "Find high-value clients for priority management"
        },
        {
            "question": "What are the top 5 attorneys by billable hours?",
            "category": "Performance Analytics",
            "description": "Identify most productive attorneys"
        },
        {
            "question": "How many cases were filed in the last 6 months?",
            "category": "Case Management",
            "description": "Track recent case activity"
        },
        {
            "question": "Show revenue by practice area",
            "category": "Financial Analysis",
            "description": "Analyze revenue distribution across practice areas"
        },
        {
            "question": "Which contracts are expiring in the next 90 days?",
            "category": "Contract Management",
            "description": "Identify contracts requiring renewal attention"
        },
        {
            "question": "What is the average case duration by case type?",
            "category": "Performance Analytics",
            "description": "Analyze case processing efficiency"
        },
        {
            "question": "Show me all cases with status 'pending'",
            "category": "Case Management",
            "description": "List all pending cases for review"
        },
        {
            "question": "Which clients have the most active cases?",
            "category": "Client Management",
            "description": "Identify clients with high case volume"
        }
    ]
    
    return {
        "success": True,
        "sample_queries": sample_queries,
        "total_queries": len(sample_queries)
    }

@router.get("/connection-status")
async def get_connection_status():
    """Get database connection status"""
    
    try:
        return {
            "connected": db_manager.is_connected(),
            "connection_info": db_manager.get_connection_info() if db_manager.is_connected() else None,
            "ollama_available": sql_generator.test_connection(),
            "chart_generator_available": chart_generator.test_connection(),
            "database_type": db_manager.db_type if db_manager.is_connected() else None
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "connected": False,
            "connection_info": None,
            "ollama_available": False,
            "chart_generator_available": False,
            "database_type": None,
            "error": str(e)
        }

@router.get("/tables")
async def get_tables():
    """Get list of available tables"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        tables = db_manager.get_tables()
        return {
            "success": True,
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        logger.error(f"Table listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/table/{table_name}/sample")
async def get_table_sample(table_name: str, limit: int = 10):
    """Get sample data from a specific table"""
    
    if not db_manager.is_connected():
        raise HTTPException(status_code=400, detail="No database connection")
    
    try:
        success, data = db_manager.get_sample_data(table_name, limit)
        
        if success:
            if hasattr(data, 'to_dict'):
                records = data.to_dict(orient='records')
                columns = list(data.columns)
            else:
                records = data
                columns = list(data[0].keys()) if data and isinstance(data[0], dict) else []
            
            return {
                "success": True,
                "table_name": table_name,
                "data": records,
                "columns": columns,
                "row_count": len(records),
                "limit": limit
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to get sample data: {data}")
            
    except Exception as e:
        logger.error(f"Sample data retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    try:
        db_connected = db_manager.is_connected()
        ollama_available = sql_generator.test_connection()
        chart_available = chart_generator.test_connection()
        
        overall_status = "healthy" if (db_connected and ollama_available and chart_available) else "degraded"
        
        return {
            "status": overall_status,
            "database": "connected" if db_connected else "disconnected",
            "ollama": "available" if ollama_available else "unavailable",
            "chart_generator": "available" if chart_available else "unavailable",
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
