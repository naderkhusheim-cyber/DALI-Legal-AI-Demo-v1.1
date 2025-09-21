#!/usr/bin/env python3
"""
Chart Generator Usage Examples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database.chart_generator import ChartGenerator
from src.utils.config import load_config
import pandas as pd

def chart_generator_examples():
    """Demonstrate chart generator usage"""
    print("📚 Chart Generator Usage Examples\n")
    
    # Load project configuration
    config = load_config('config/config.yaml')
    
    # Create chart generator
    generator = ChartGenerator(config)
    
    # Example 1: Basic bar chart
    print("1️⃣ Basic Bar Chart:")
    sample_data = pd.DataFrame({
        'client_name': ['TechCorp Inc.', 'Smith Industries', 'Johnson LLC', 'Davis Enterprises'],
        'case_count': [15, 8, 12, 6],
        'revenue': [250000, 180000, 120000, 90000]
    })
    
    result = generator.generate_chart(sample_data, "Show client case counts")
    if result['success']:
        print(f"   ✅ Chart type: {result['chart_config']['chart_type']}")
        print(f"   📊 Title: {result['chart_config']['title']}")
        print(f"   💭 Reasoning: {result['reasoning']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Example 2: Revenue comparison
    print("\n2️⃣ Revenue Comparison Chart:")
    result = generator.generate_chart(sample_data, "Compare client revenue")
    if result['success']:
        print(f"   ✅ Chart type: {result['chart_config']['chart_type']}")
        print(f"   📊 Title: {result['chart_config']['title']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Example 3: Practice area distribution
    print("\n3️⃣ Practice Area Distribution:")
    practice_data = pd.DataFrame({
        'practice_area': ['Corporate Law', 'Litigation', 'IP Law', 'Real Estate', 'Tax Law'],
        'attorney_count': [3, 2, 1, 1, 1],
        'avg_hourly_rate': [450, 525, 400, 425, 500]
    })
    
    result = generator.generate_chart(practice_data, "Show practice area distribution")
    if result['success']:
        print(f"   ✅ Chart type: {result['chart_config']['chart_type']}")
        print(f"   📊 Title: {result['chart_config']['title']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Example 4: Time series data
    print("\n4️⃣ Time Series Chart:")
    time_data = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'cases_filed': [5, 8, 12, 7, 9, 11],
        'revenue': [50000, 80000, 120000, 70000, 90000, 110000]
    })
    
    result = generator.generate_chart(time_data, "Show cases filed over time")
    if result['success']:
        print(f"   ✅ Chart type: {result['chart_config']['chart_type']}")
        print(f"   📊 Title: {result['chart_config']['title']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Example 5: Statistical data
    print("\n5️⃣ Statistical Chart:")
    stats_data = pd.DataFrame({
        'case_value': [25000, 50000, 75000, 100000, 125000, 150000, 200000, 300000, 500000, 750000],
        'case_duration_days': [30, 45, 60, 90, 120, 150, 180, 240, 300, 365]
    })
    
    result = generator.generate_chart(stats_data, "Show case value vs duration correlation")
    if result['success']:
        print(f"   ✅ Chart type: {result['chart_config']['chart_type']}")
        print(f"   📊 Title: {result['chart_config']['title']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print("\n✅ All chart generator examples completed!")

if __name__ == "__main__":
    chart_generator_examples()
