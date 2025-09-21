"""
Chart Generator for Legal Data Visualization
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import requests
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generates charts from query results using AI recommendations"""
    
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
            self.model = os.getenv('CHART_GENERATION_MODEL', 'llama3.2:1b')
        
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
    
    def generate_chart(self, df: pd.DataFrame, user_query: str) -> Dict[str, Any]:
        """Generate appropriate chart based on data and user intent"""
        
        if df.empty:
            return {'success': False, 'error': 'No data to visualize'}
        
        try:
            # Get AI recommendation for chart type
            chart_config = self._get_chart_recommendation(df, user_query)
            
            # Create the chart
            chart_result = self._create_chart(df, chart_config)
            
            if chart_result['success']:
                return {
                    'success': True,
                    'chart_html': chart_result['chart_html'],
                    'chart_config': chart_config,
                    'reasoning': chart_config.get('reasoning', 'Chart generated based on data structure')
                }
            else:
                return chart_result
                
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_chart_recommendation(self, df: pd.DataFrame, user_query: str) -> Dict[str, Any]:
        """Get AI recommendation for chart type"""
        
        columns_info = list(df.columns)
        data_types = {col: str(df[col].dtype) for col in df.columns}
        data_sample = df.head(3).to_dict() if len(df) > 0 else {}
        
        prompt = f"""
You are a data visualization expert for legal data. Based on the data structure and user question, recommend the best chart type and configuration.

Available Columns: {columns_info}
Data Types: {data_types}
Data Sample: {str(data_sample)[:500]}
User Question: {user_query}

Respond with a JSON object containing:
{{
    "chart_type": "bar|line|pie|scatter|histogram|box|heatmap",
    "x_column": "column_name",
    "y_column": "column_name", 
    "color_column": "column_name_or_null",
    "title": "Chart Title",
    "reasoning": "Why this chart type is appropriate for legal data"
}}

Consider:
- Bar charts for categorical comparisons
- Line charts for trends over time
- Pie charts for proportions
- Scatter plots for correlations
- Histograms for distributions
- Box plots for statistical summaries
- Heatmaps for correlation matrices
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "max_tokens": 300
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                try:
                    # Clean the response to extract JSON
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        return json.loads(json_str)
                    else:
                        return self._create_default_chart_config(df, user_query)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error: {e}")
                    return self._create_default_chart_config(df, user_query)
            else:
                logger.warning(f"Ollama API error: {response.status_code}")
                return self._create_default_chart_config(df, user_query)
                
        except requests.exceptions.Timeout:
            logger.warning("Ollama API timeout")
            return self._create_default_chart_config(df, user_query)
        except Exception as e:
            logger.warning(f"Chart recommendation error: {e}")
            return self._create_default_chart_config(df, user_query)
    
    def _create_default_chart_config(self, df: pd.DataFrame, user_query: str = "") -> Dict[str, Any]:
        """Create default chart configuration based on data types"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Determine chart type based on data structure
        if len(numeric_cols) >= 1 and len(text_cols) >= 1:
            chart_type = "bar"
            x_col = text_cols[0]
            y_col = numeric_cols[0]
            title = f"{numeric_cols[0]} by {text_cols[0]}"
            reasoning = "Bar chart selected for categorical vs numeric data"
        elif len(numeric_cols) >= 2:
            chart_type = "scatter"
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            title = f"{numeric_cols[1]} vs {numeric_cols[0]}"
            reasoning = "Scatter plot selected for numeric vs numeric data"
        elif len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
            chart_type = "line"
            x_col = datetime_cols[0]
            y_col = numeric_cols[0]
            title = f"{numeric_cols[0]} over time"
            reasoning = "Line chart selected for time series data"
        elif len(numeric_cols) >= 1:
            chart_type = "histogram"
            x_col = numeric_cols[0]
            y_col = None
            title = f"Distribution of {numeric_cols[0]}"
            reasoning = "Histogram selected for numeric data distribution"
        else:
            chart_type = "bar"
            x_col = df.columns[0]
            y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            title = "Data Visualization"
            reasoning = "Default bar chart configuration"
        
        return {
            "chart_type": chart_type,
            "x_column": x_col,
            "y_column": y_col,
            "color_column": None,
            "title": title,
            "reasoning": reasoning
        }
    
    def _create_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Plotly chart based on configuration"""
        
        try:
            chart_type = config.get('chart_type', 'bar')
            x_col = config.get('x_column')
            y_col = config.get('y_column') 
            color_col = config.get('color_column')
            title = config.get('title', 'Legal Data Visualization')
            
            # Validate columns exist
            if x_col and x_col not in df.columns:
                x_col = df.columns[0]
            if y_col and y_col not in df.columns:
                y_col = df.columns[1] if len(df.columns) > 1 else None
            if color_col and color_col not in df.columns:
                color_col = None
            
            # Create appropriate chart
            if chart_type == "bar":
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "line":
                fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col, title=title)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "histogram":
                fig = px.histogram(df, x=x_col, color=color_col, title=title)
            elif chart_type == "box":
                fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == "heatmap":
                # Create correlation heatmap for numeric columns
                numeric_df = df.select_dtypes(include=['number'])
                if len(numeric_df.columns) > 1:
                    corr_matrix = numeric_df.corr()
                    fig = px.imshow(corr_matrix, title=title, aspect="auto")
                else:
                    fig = px.bar(df, x=x_col, y=y_col, title=title)
            else:
                fig = px.bar(df, x=x_col, y=y_col, title=title)
            
            # Customize for legal theme
            fig.update_layout(
                template="plotly_white",
                font=dict(family="Arial", size=12),
                title_font=dict(size=16, color="darkblue"),
                xaxis_title_font=dict(size=14),
                yaxis_title_font=dict(size=14),
                height=500,
                margin=dict(l=50, r=50, t=80, b=50),
                showlegend=True
            )
            
            # Add legal-themed colors
            if chart_type in ["bar", "line", "scatter"]:
                fig.update_traces(
                    marker_color='#1f77b4',
                    marker_line_color='#2c3e50',
                    marker_line_width=1
                )
            
            # Convert to HTML
            chart_html = fig.to_html(include_plotlyjs='cdn', div_id="chart")
            
            return {
                'success': True,
                'chart_html': chart_html
            }
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            return {
                'success': False,
                'error': f"Chart creation failed: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
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

# Convenience function to create a chart generator instance
def create_chart_generator(config: Dict[str, Any] = None) -> ChartGenerator:
    """Create a new ChartGenerator instance"""
    return ChartGenerator(config)

# Test function
def test_chart_generator():
    """Test the chart generator functionality"""
    print("🧪 Testing Chart Generator...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'client_name': ['TechCorp Inc.', 'Smith Industries', 'Johnson LLC', 'Davis Enterprises'],
        'case_count': [15, 8, 12, 6],
        'revenue': [250000, 180000, 120000, 90000],
        'practice_area': ['Corporate', 'Litigation', 'IP', 'Real Estate']
    })
    
    generator = ChartGenerator()
    
    # Test connection
    if generator.test_connection():
        print("✅ Ollama connection successful")
        
        # Test chart generation
        result = generator.generate_chart(sample_data, "Show client revenue comparison")
        
        if result['success']:
            print("✅ Chart generated successfully")
            print(f"   Chart type: {result['chart_config']['chart_type']}")
            print(f"   Title: {result['chart_config']['title']}")
            print(f"   Reasoning: {result['reasoning']}")
        else:
            print(f"❌ Chart generation failed: {result['error']}")
        
        print("✅ Chart Generator test completed successfully")
    else:
        print("❌ Failed to connect to Ollama")

if __name__ == "__main__":
    test_chart_generator()
